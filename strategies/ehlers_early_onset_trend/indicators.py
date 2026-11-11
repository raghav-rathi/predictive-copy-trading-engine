"""John Ehlers' Early Onset Trend indicators.

"The Quotient Transform", TASC August 2014 (TradeStation Traders'
Tips, Aug 2014 — the article the brief dates to 2016 is in fact the
August 2014 issue). A roofing filter (2-pole high-pass with a 100-bar
cutoff, removing spectral dilation) feeds a SuperSmoother (LPPeriod
30); the result is normalised by a fast-attack / slow-decay peak
tracker (automatic gain control) and passed through the quotient
transform twice, with K1 = 0.85 and K2 = 0.4:

    alpha1 = (cos(0.707*360/100) + sin(0.707*360/100) - 1)
             / cos(0.707*360/100)
    HP[i]   = (1-alpha1/2)^2 * (C[i] - 2*C[i-1] + C[i-2])
              + 2*(1-alpha1)*HP[i-1] - (1-alpha1)^2*HP[i-2]
    a1 = exp(-1.414*pi/30); b1 = 2*a1*cos(1.414*180/30)
    c2 = b1; c3 = -a1^2; c1 = 1 - c2 - c3
    Filt[i] = c1*(HP[i] + HP[i-1])/2 + c2*Filt[i-1] + c3*Filt[i-2]
    Peak[i] = 0.991*Peak[i-1]; if |Filt[i]| > Peak[i]: Peak[i] = |Filt[i]|
    X[i]    = Filt[i] / Peak[i]            (0 while Peak is 0)
    Q1[i]   = (X[i] + 0.85) / (0.85*X[i] + 1)
    Q2[i]   = (X[i] + 0.40) / (0.40*X[i] + 1)

Quotient values near +1 signify uptrend, near -1 downtrend. Bars
before the second difference exists (i < 2) have HP = Filt = 0, so
X = 0 and Q1 = 0.85 / Q2 = 0.40 exactly — matching the EasyLanguage
variables, which initialise to 0.

All computation is causal: every value on bar i uses only data
through bar i's close.
"""

import math

import numpy as np
import pandas as pd

HP_PERIOD = 100  # high-pass cutoff (spectral dilation limit)
LP_PERIOD = 30   # SuperSmoother period
K1 = 0.85
K2 = 0.40
PEAK_DECAY = 0.991

_ALPHA1 = (
    math.cos(math.radians(0.707 * 360 / HP_PERIOD))
    + math.sin(math.radians(0.707 * 360 / HP_PERIOD))
    - 1
) / math.cos(math.radians(0.707 * 360 / HP_PERIOD))

_A1 = math.exp(-1.414 * math.pi / LP_PERIOD)
_B1 = 2 * _A1 * math.cos(math.radians(1.414 * 180 / LP_PERIOD))
_C2 = _B1
_C3 = -_A1 * _A1
_C1 = 1 - _C2 - _C3

INDICATOR_COLS = ["hp", "filt", "peak", "x", "q1", "q2"]


def eot_coefs() -> dict:
    """Published Early Onset Trend coefficients for the shipped parameters."""
    return {
        "alpha1": _ALPHA1,
        "a1": _A1,
        "b1": _B1,
        "c1": _C1,
        "c2": _C2,
        "c3": _C3,
        "k1": K1,
        "k2": K2,
        "peak_decay": PEAK_DECAY,
    }


def _eot_filter(close: np.ndarray) -> dict[str, np.ndarray]:
    """Exact published HP -> SuperSmoother -> Peak -> quotient recursion."""
    n = len(close)
    hp = np.zeros(n)
    filt = np.zeros(n)
    peak = np.zeros(n)
    x = np.zeros(n)
    for i in range(n):
        if i >= 2:
            hp[i] = (
                (1 - _ALPHA1 / 2) ** 2 * (close[i] - 2 * close[i - 1] + close[i - 2])
                + 2 * (1 - _ALPHA1) * hp[i - 1]
                - (1 - _ALPHA1) ** 2 * hp[i - 2]
            )
            filt[i] = (
                _C1 * (hp[i] + hp[i - 1]) / 2
                + _C2 * filt[i - 1]
                + _C3 * filt[i - 2]
            )
        peak[i] = PEAK_DECAY * (peak[i - 1] if i >= 1 else 0.0)
        if abs(filt[i]) > peak[i]:
            peak[i] = abs(filt[i])
        x[i] = filt[i] / peak[i] if peak[i] != 0 else 0.0
    q1 = (x + K1) / (K1 * x + 1)
    q2 = (x + K2) / (K2 * x + 1)
    return {"hp": hp, "filt": filt, "peak": peak, "x": x, "q1": q1, "q2": q2}


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    out = _eot_filter(df["c"].to_numpy(dtype=float))
    for col in INDICATOR_COLS:
        df[col] = out[col]
    return df
