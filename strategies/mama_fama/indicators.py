"""John Ehlers MESA Adaptive Moving Average (MAMA/FAMA) indicators.

Ehlers' MAMA adapts its smoothing alpha to the market's measured cycle
period. A Hilbert-transform discriminator (detrender -> quadrature
pair I1/Q1 -> 90-degree-shifted jI/jQ -> smoothed I2/Q2 phasor ->
phase-advance Re/Im -> 360/atan(Im/Re)) estimates the dominant cycle
period each bar, clamped to [6, 50] and to a 0.67x-1.5x walk from the
prior bar's period. From the period ratio:

    deltaPhase = period[i-1] / period[i]
    alpha      = clamp(fast_limit / deltaPhase, slow_limit=0.05, fast_limit)

so alpha opens up (fast) when the cycle shortens and tightens (slow)
when it lengthens. MAMA tracks with that alpha; FAMA is a half-alpha
smoothed MAMA.

Recurrence below follows Ehlers' original code verbatim. ``[k]`` is a
lag of k bars; lags before bar 0 are clamped to bar 0's value. No
lookahead: every value at bar i uses only data through bar i.

Added columns:
  mama        -- MESA Adaptive Moving Average
  fama        -- Following Adaptive Moving Average (half-alpha of MAMA)
  mama_alpha  -- adaptive alpha used on that bar (in [0.05, fast_limit])
  mama_period -- measured dominant-cycle period (clamped [6, 50])
  atr         -- Wilder ATR(14) for the risk harness
"""

import numpy as np
import pandas as pd

from strategies import base as B

SLOW_LIMIT = 0.05
PERIOD_MIN = 6.0
PERIOD_MAX = 50.0
PERIOD_INIT = 20.0
ATR_N = 14


def _clamp(x, lo, hi):
    return lo if x < lo else (hi if x > hi else x)


def _mama_fama(price: np.ndarray, fast_limit: float):
    """Single causal numpy loop. Returns (mama, fama, alpha, period)."""
    n = len(price)
    mama = np.full(n, np.nan)
    fama = np.full(n, np.nan)
    alpha_a = np.full(n, np.nan)
    period_a = np.full(n, np.nan)
    if n == 0:
        return mama, fama, alpha_a, period_a

    smooth = np.zeros(n)
    detr = np.zeros(n)
    q1 = np.zeros(n)
    i1 = np.zeros(n)
    ji = np.zeros(n)
    jq = np.zeros(n)
    i2 = np.zeros(n)
    q2 = np.zeros(n)
    re = np.zeros(n)
    im = np.zeros(n)
    period = np.zeros(n)
    alpha = np.zeros(n)
    m = np.zeros(n)
    f = np.zeros(n)

    def g(arr, i, k):
        # lag k, clamped to the first available value
        j = i - k
        return arr[j] if j >= 0 else arr[0]

    # seeds hold at bar 0 (the loop's clamped lags read them as "previous" values)
    m[0] = price[0]
    f[0] = price[0]
    period[0] = PERIOD_INIT
    alpha[0] = _clamp(float(fast_limit), SLOW_LIMIT, fast_limit)
    for i in range(n):
        if i == 0:
            # filter lags all clamp to bar 0 -> detrender coeffs sum to zero,
            # so im[0] == re[0] == 0 and the seeds above are preserved
            smooth[i] = price[i]
            continue
        p = price[i]
        pp = g(period, i, 1)
        adj = 0.075 * pp + 0.54
        smooth[i] = (4.0 * p + 3.0 * g(price, i, 1)
                     + 2.0 * g(price, i, 2) + g(price, i, 3)) / 10.0
        detr[i] = (0.0962 * smooth[i] + 0.5769 * g(smooth, i, 2)
                   - 0.5769 * g(smooth, i, 4) - 0.0962 * g(smooth, i, 6)) * adj
        q1[i] = (0.0962 * detr[i] + 0.5769 * g(detr, i, 2)
                 - 0.5769 * g(detr, i, 4) - 0.0962 * g(detr, i, 6)) * adj
        i1[i] = g(detr, i, 3)
        ji[i] = (0.0962 * i1[i] + 0.5769 * g(i1, i, 2)
                 - 0.5769 * g(i1, i, 4) - 0.0962 * g(i1, i, 6)) * adj
        jq[i] = (0.0962 * q1[i] + 0.5769 * g(q1, i, 2)
                 - 0.5769 * g(q1, i, 4) - 0.0962 * g(q1, i, 6)) * adj
        i2[i] = 0.2 * (i1[i] - jq[i]) + 0.8 * g(i2, i, 1)
        q2[i] = 0.2 * (q1[i] + ji[i]) + 0.8 * g(q2, i, 1)
        re[i] = 0.2 * (i2[i] * g(i2, i, 1) + q2[i] * g(q2, i, 1)) + 0.8 * g(re, i, 1)
        im[i] = 0.2 * (i2[i] * g(q2, i, 1) - q2[i] * g(i2, i, 1)) + 0.8 * g(im, i, 1)
        if im[i] != 0.0 and re[i] != 0.0:
            pv = 360.0 / np.arctan(im[i] / re[i])
            pv = _clamp(pv, 0.67 * pp, 1.5 * pp)
            pv = _clamp(pv, PERIOD_MIN, PERIOD_MAX)
            period[i] = pv
        else:
            period[i] = pp
        delta_phase = pp / period[i] if period[i] != 0.0 else 1.0
        a = _clamp(fast_limit / delta_phase, SLOW_LIMIT, fast_limit)
        alpha[i] = a
        m[i] = a * p + (1.0 - a) * g(m, i, 1)
        f[i] = 0.5 * a * m[i] + (1.0 - 0.5 * a) * g(f, i, 1)

    return m, f, alpha, period


def add_indicators(df: pd.DataFrame, fast_limit: float = 0.5) -> pd.DataFrame:
    df = df.copy()
    price = ((df["h"] + df["l"]) / 2).to_numpy(dtype=float)
    mama, fama, alpha_a, period_a = _mama_fama(price, float(fast_limit))
    df["mama"] = mama
    df["fama"] = fama
    df["mama_alpha"] = alpha_a
    df["mama_period"] = period_a
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
