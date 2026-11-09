"""Ehlers MESA Adaptive Moving Average (MAMA) / FAMA indicators.

Faithful transcription of the MAMA algorithm from John F. Ehlers,
"Rocket Science for Traders: Digital Signal Processing Applications"
(John Wiley & Sons, ISBN 0471405671), as published in his paper
"MAMA - The Mother of Adaptive Moving Averages"
(https://mesasoftware.com/papers/MAMA.pdf) and implemented in TA-Lib
(https://ta-lib.org/functions/mama.html, ``ta_MAMA.c``).

Pipeline (all causal, bar i uses only data through bar i):
  price = (h + l) / 2  (Ehlers' EasyLanguage input Price((H+L)/2))
  detrender = (0.0962*price + 0.5769*price[-2] - 0.5769*price[-4]
               - 0.0962*price[-6]) * (0.075*period_prev + 0.54)
  Q1 = same Hilbert FIR applied to detrender (quadrature component)
  I1 = detrender[-3]  (in-phase component)
  jI, jQ = same FIR applied to Q1 and I1 (homodyne discriminator)
  I2 = I1 - jQ; Q2 = Q1 + jI; both smoothed 0.2/0.8
  Re = I2*I2_prev + Q2*Q2_prev; Im = I2*Q2_prev - Q2*I2_prev
  (Re, Im smoothed 0.2/0.8)
  period = 360 / atan(Im/Re) degrees, clamped to 1.5x/0.67x of the
  previous period, then to [6, 50], then smoothed 0.2/0.8
  phase = atan(Q1/I1) in degrees (+180 if I1 < 0)
  deltaPhase = max(1, phase_prev - phase)
  alpha = clamp(fastLimit / deltaPhase, slowLimit, fastLimit)
  MAMA = alpha*price + (1-alpha)*MAMA_prev
  FAMA = (alpha/2)*MAMA + (1-alpha/2)*FAMA_prev

Fast limit 0.5, slow limit 0.05 (Ehlers' suggested values). The first
32 bars are NaN (TA-Lib's initial unstable period); history before bar
0 is treated as zero, matching TA-Lib's zero-initialised buffers.
"""

import math

import numpy as np
import pandas as pd

FAST_LIMIT = 0.5
SLOW_LIMIT = 0.05
LOOKBACK = 32  # TA-Lib initial unstable period for MAMA

INDICATOR_COLS = [
    "mama",
    "fama",
    "mama_alpha",
    "mama_period",
]


def _at(hist: list, j: int) -> float:
    """hist[j] with zero for out-of-range (pre-start) indices."""
    return hist[j] if 0 <= j < len(hist) else 0.0


def _mama_fama(price: np.ndarray):
    """Run the MAMA recursion. Returns (mama, fama, alpha, period)."""
    n = len(price)
    mama = np.full(n, np.nan)
    fama = np.full(n, np.nan)
    alpha_out = np.full(n, np.nan)
    period_out = np.full(n, np.nan)

    det_hist: list[float] = []
    q1_hist: list[float] = []
    i1_hist: list[float] = []

    prev_period = 0.0
    prev_smooth_period = 0.0
    prev_i2 = 0.0
    prev_q2 = 0.0
    prev_re = 0.0
    prev_im = 0.0
    prev_phase = 0.0
    prev_mama: float | None = None
    prev_fama: float | None = None

    for i in range(n):
        p = float(price[i])
        factor = 0.075 * prev_period + 0.54
        p2 = float(price[i - 2]) if i >= 2 else 0.0
        p4 = float(price[i - 4]) if i >= 4 else 0.0
        p6 = float(price[i - 6]) if i >= 6 else 0.0

        det = (0.0962 * p + 0.5769 * p2 - 0.5769 * p4 - 0.0962 * p6) * factor
        det_hist.append(det)
        q1 = (
            0.0962 * det
            + 0.5769 * _at(det_hist, i - 2)
            - 0.5769 * _at(det_hist, i - 4)
            - 0.0962 * _at(det_hist, i - 6)
        ) * factor
        q1_hist.append(q1)
        i1 = _at(det_hist, i - 3)
        i1_hist.append(i1)
        ji = (
            0.0962 * q1
            + 0.5769 * _at(q1_hist, i - 2)
            - 0.5769 * _at(q1_hist, i - 4)
            - 0.0962 * _at(q1_hist, i - 6)
        ) * factor
        jq = (
            0.0962 * i1
            + 0.5769 * _at(i1_hist, i - 2)
            - 0.5769 * _at(i1_hist, i - 4)
            - 0.0962 * _at(i1_hist, i - 6)
        ) * factor

        i2 = i1 - jq
        q2 = q1 + ji
        i2 = 0.2 * i2 + 0.8 * prev_i2
        q2 = 0.2 * q2 + 0.8 * prev_q2
        re = i2 * prev_i2 + q2 * prev_q2
        im = i2 * prev_q2 - q2 * prev_i2
        re = 0.2 * re + 0.8 * prev_re
        im = 0.2 * im + 0.8 * prev_im

        if im != 0.0 and re != 0.0:
            period = 360.0 / math.atan(im / re)
        else:
            period = 0.0
        if period > 1.5 * prev_period:
            period = 1.5 * prev_period
        elif period < 0.67 * prev_period:
            period = 0.67 * prev_period
        if period < 6.0:
            period = 6.0
        elif period > 50.0:
            period = 50.0
        period = 0.2 * period + 0.8 * prev_period
        smooth_period = 0.33 * period + 0.67 * prev_smooth_period

        if q1 != 0.0 and i1 != 0.0:
            phase = math.atan(q1 / i1) * 57.29577951308232
            if i1 < 0.0:
                phase += 180.0
        else:
            phase = 0.0
        delta_phase = prev_phase - phase
        if delta_phase < 1.0:
            delta_phase = 1.0
        alpha = FAST_LIMIT / delta_phase
        if alpha < SLOW_LIMIT:
            alpha = SLOW_LIMIT
        elif alpha > FAST_LIMIT:
            alpha = FAST_LIMIT

        if prev_mama is None:
            mama_i = p
            fama_i = p
        else:
            mama_i = alpha * p + (1.0 - alpha) * prev_mama
            fama_i = 0.5 * alpha * mama_i + (1.0 - 0.5 * alpha) * prev_fama

        prev_period = period
        prev_smooth_period = smooth_period
        prev_i2, prev_q2 = i2, q2
        prev_re, prev_im = re, im
        prev_phase = phase
        prev_mama, prev_fama = mama_i, fama_i

        if i >= LOOKBACK:
            mama[i] = mama_i
            fama[i] = fama_i
            alpha_out[i] = alpha
            period_out[i] = period

    return mama, fama, alpha_out, period_out


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    price = ((df["h"] + df["l"]) / 2).to_numpy(dtype=float)
    mama, fama, alpha, period = _mama_fama(price)
    df["mama"] = mama
    df["fama"] = fama
    df["mama_alpha"] = alpha
    df["mama_period"] = period
    return df
