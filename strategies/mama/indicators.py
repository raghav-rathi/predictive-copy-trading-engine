"""John Ehlers MESA Adaptive Moving Average (MAMA/FAMA) indicators.

MAMA (Ehlers, "MESA Adaptive Moving Averages", TASC Sep 2001;
*Cybernetic Analysis for Stocks and Futures*, 2004) adapts its
smoothing alpha to the market's measured cycle phase rate of change,
estimated with a truncated Hilbert transform. The chain below follows
Ehlers' original EasyLanguage code (as in TA-Lib's TA_MAMA) verbatim:

    price       = (H + L) / 2
    Smooth      = (4*P + 3*P[1] + 2*P[2] + P[3]) / 10
    Detrender   = HT(Smooth)
    Q1          = HT(Detrender)
    I1          = Detrender[3]
    jI          = HT(I1),  jQ = HT(Q1)
    I2          = 0.2*(I1 - jQ) + 0.8*I2[1]
    Q2          = 0.2*(Q1 + jI) + 0.8*Q2[1]
    Re          = I2*I2[1] + Q2*Q2[1]
    Im          = I2*Q2[1] - Q2*I2[1]
    Period      = 360 / atan_deg(Im / Re), walk-clamped to
                  [0.67, 1.5] x previous period, clamped to [6, 50],
                  then 0.2*Period + 0.8*Period[1]
    Phase       = atan_deg(Q1 / I1)          (one-arg atan, -90..90 deg)
    DeltaPhase  = max(1, Phase[1] - Phase)
    alpha       = clamp(FastLimit / DeltaPhase, SlowLimit, FastLimit)
                  with FastLimit = 0.5, SlowLimit = 0.05
    MAMA        = alpha*price + (1 - alpha)*MAMA[1]
    FAMA        = 0.5*alpha*MAMA + (1 - 0.5*alpha)*FAMA[1]

where HT(x) is Ehlers' 7-tap Hilbert transformer on the lagged series:

    HT(x)[t] = (0.0962*x[t] + 0.5769*x[t-2] - 0.5769*x[t-4]
                - 0.0962*x[t-6]) * (0.075*Period[t-1] + 0.54)

Lags before bar 0 are clamped to bar 0's value; MAMA/FAMA are seeded
at the first price. Early bars are spin-up garbage by construction --
WARMUP (100) keeps them out of the backtest.

Columns:

    mama_smooth, mama_detrender -- intermediate Hilbert chain states
    mama_i1, mama_q1            -- in-phase / quadrature components
    mama_period                 -- measured dominant-cycle period [6, 50]
    mama_phase                  -- cycle phase in degrees (-90..90)
    mama_alpha                  -- adaptive alpha in [0.05, 0.5]
    mama, fama                  -- the two adaptive averages
    atr                         -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses only data through bar i's
close (all lags are backward-looking).
"""

import math

import numpy as np
import pandas as pd

from strategies import base as B

FAST_LIMIT = 0.5
SLOW_LIMIT = 0.05
PERIOD_MIN = 6.0
PERIOD_MAX = 50.0
PERIOD_INIT = 20.0
ATR_N = 14

INDICATOR_COLS = [
    "mama_smooth",
    "mama_detrender",
    "mama_i1",
    "mama_q1",
    "mama_period",
    "mama_phase",
    "mama_alpha",
    "mama",
    "fama",
    "atr",
]


def _lag(x, i, k):
    """x[i - k] with lags before bar 0 clamped to x[0]."""
    return x[i - k] if i - k >= 0 else x[0]


def _hilbert(x, i, period_prev):
    """Ehlers' 7-tap Hilbert transformer at bar i."""
    return (
        0.0962 * _lag(x, i, 0)
        + 0.5769 * _lag(x, i, 2)
        - 0.5769 * _lag(x, i, 4)
        - 0.0962 * _lag(x, i, 6)
    ) * (0.075 * period_prev + 0.54)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    price = ((df["h"] + df["l"]) / 2).to_numpy(dtype=float)
    n = len(df)

    smooth = np.zeros(n)
    detrender = np.zeros(n)
    q1 = np.zeros(n)
    i1 = np.zeros(n)
    i2 = np.zeros(n)
    q2 = np.zeros(n)
    period = np.full(n, np.nan)
    phase = np.zeros(n)
    alpha = np.full(n, np.nan)
    mama = np.full(n, np.nan)
    fama = np.full(n, np.nan)

    period_prev = PERIOD_INIT
    smooth_period_prev = PERIOD_INIT
    i2_prev = 0.0
    q2_prev = 0.0
    phase_prev = 0.0
    mama_prev = price[0] if n else 0.0
    fama_prev = price[0] if n else 0.0

    for i in range(n):
        p = price[i]
        smooth[i] = (
            4.0 * _lag(price, i, 0)
            + 3.0 * _lag(price, i, 1)
            + 2.0 * _lag(price, i, 2)
            + 1.0 * _lag(price, i, 3)
        ) / 10.0

        detrender[i] = _hilbert(smooth, i, period_prev)
        # Float hygiene: the Hilbert taps sum to exactly zero, so on
        # constant input the detrender is analytically 0 and any
        # |value| < 1e-12 is pure round-off residue. Left unsnapped,
        # that residue makes the phase jump around and fires spurious
        # MAMA/FAMA crosses on flat stretches. 1e-12 is 7+ orders of
        # magnitude below any real detrender value, so real data is
        # unaffected; only the exact-zero case is cleaned up.
        if abs(detrender[i]) < 1e-12:
            detrender[i] = 0.0
        q1[i] = _hilbert(detrender, i, period_prev)
        i1[i] = _lag(detrender, i, 3)
        ji = _hilbert(i1, i, period_prev)
        jq = _hilbert(q1, i, period_prev)

        i2[i] = 0.2 * (i1[i] - jq) + 0.8 * i2_prev
        q2[i] = 0.2 * (q1[i] + ji) + 0.8 * q2_prev

        # Homodyne discriminator -> instantaneous period.
        re = i2[i] * i2_prev + q2[i] * q2_prev
        im = i2[i] * q2_prev - q2[i] * i2_prev
        period_i = period_prev
        if im != 0.0 and re != 0.0:
            period_i = 360.0 / math.degrees(math.atan(im / re))
            if period_i > 1.5 * period_prev:
                period_i = 1.5 * period_prev
            if period_i < 0.67 * period_prev:
                period_i = 0.67 * period_prev
            if period_i < PERIOD_MIN:
                period_i = PERIOD_MIN
            if period_i > PERIOD_MAX:
                period_i = PERIOD_MAX
            period_i = 0.2 * period_i + 0.8 * period_prev
        period[i] = period_i
        smooth_period_prev = 0.33 * period_i + 0.67 * smooth_period_prev

        # Phase rate of change -> adaptive alpha.
        if i1[i] != 0.0:
            phase[i] = math.degrees(math.atan(q1[i] / i1[i]))
        else:
            phase[i] = 0.0
        delta_phase = phase_prev - phase[i]
        if delta_phase < 1.0:
            delta_phase = 1.0
        a = FAST_LIMIT / delta_phase
        if a < SLOW_LIMIT:
            a = SLOW_LIMIT
        if a > FAST_LIMIT:
            a = FAST_LIMIT
        alpha[i] = a

        mama[i] = a * p + (1.0 - a) * mama_prev
        fama[i] = 0.5 * a * mama[i] + (1.0 - 0.5 * a) * fama_prev

        period_prev = period_i
        i2_prev = i2[i]
        q2_prev = q2[i]
        phase_prev = phase[i]
        mama_prev = mama[i]
        fama_prev = fama[i]

    df["mama_smooth"] = smooth
    df["mama_detrender"] = detrender
    df["mama_i1"] = i1
    df["mama_q1"] = q1
    df["mama_period"] = period
    df["mama_phase"] = phase
    df["mama_alpha"] = alpha
    df["mama"] = mama
    df["fama"] = fama
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
