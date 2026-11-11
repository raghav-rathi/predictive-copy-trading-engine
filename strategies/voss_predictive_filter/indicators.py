"""John Ehlers' Voss Predictive Filter indicators.

"A Peek Into The Future", TASC August 2019. A 2-pole band-pass filter
isolates the cyclic component around a 20-bar cycle, then Henning
Voss's negative-group-delay predictor advances its phase so peaks and
zero-crossings appear before the corresponding events in the band-pass
output. Exact published recursion (TradeStation Traders' Tips, Aug 2019):

    Bandwidth = 0.25, Order = 3 * Predict = 9
    F1 = cos(2*pi / Period)
    G1 = cos(Bandwidth * 2*pi / Period)
    S1 = 1/G1 - sqrt(1/G1^2 - 1)
    Filt[i] = 0.5*(1-S1)*(Close[i] - Close[i-2])
              + F1*(1+S1)*Filt[i-1] - S1*Filt[i-2]   (0 for the first 6 bars)
    SumC[i] = sum over Count=0..Order-1 of ((Count+1)/Order) * Voss[i-(Order-Count)]
    Voss[i] = ((3 + Order)/2) * Filt[i] - SumC[i]

The "bandpass" column is the Filt line itself — it is the same 2-pole
band-pass recursion the Wealth-Lab Traders' Tip plots as the lagging
line (BandPass.Series(Close, 20)). ADX(14) is the shared Wilder ADX
primitive, used by the entry gate.

All computation is causal: every value on bar i uses only data through
bar i's close (Voss[i] uses only Voss lags 1..9).
"""

import math

import numpy as np
import pandas as pd

from strategies.base import adx

PERIOD = 20
PREDICT = 3
BANDWIDTH = 0.25
ORDER = 3 * PREDICT  # 9

_F1 = math.cos(2 * math.pi / PERIOD)
_G1 = math.cos(BANDWIDTH * 2 * math.pi / PERIOD)
_S1 = 1 / _G1 - math.sqrt(1 / (_G1 * _G1) - 1)

INDICATOR_COLS = ["bandpass", "voss", "adx"]


def voss_coefs() -> dict:
    """Published Voss filter coefficients for the shipped parameters."""
    return {"f1": _F1, "g1": _G1, "s1": _S1, "order": ORDER}


def _voss_filter(close: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Exact published Filt/Voss recursion (numpy loop, causal)."""
    n = len(close)
    filt = np.zeros(n)
    voss = np.zeros(n)
    for i in range(n):
        if i > 5:
            filt[i] = (
                0.5 * (1 - _S1) * (close[i] - close[i - 2])
                + _F1 * (1 + _S1) * filt[i - 1]
                - _S1 * filt[i - 2]
            )
        sum_c = 0.0
        for count in range(ORDER):
            lag = ORDER - count
            if i - lag >= 0:
                sum_c += ((count + 1) / ORDER) * voss[i - lag]
        voss[i] = ((3 + ORDER) / 2) * filt[i] - sum_c
    return filt, voss


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    filt, voss = _voss_filter(df["c"].to_numpy(dtype=float))
    df["bandpass"] = filt
    df["voss"] = voss
    df["adx"] = adx(df["h"], df["l"], df["c"], 14)["adx"]
    return df
