"""Chaikin Oscillator indicators (Marc Chaikin).

Money Flow Volume: MFV = ((c - l) - (h - c)) / (h - l) * v
(0 when h == l). Accumulation/Distribution Line: ADL = cumulative
sum of MFV. Chaikin Oscillator: CHO = EMA(3, ADL) - EMA(10, ADL).
Trend filter: SMA(50) of close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

INDICATOR_COLS = [
    "co_mfv",
    "co_adl",
    "co_cho",
    "sma50",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h, l, c, v = df["h"], df["l"], df["c"], df["v"]
    rng = h - l
    mfm = np.where(rng > 0, ((c - l) - (h - c)) / rng.replace(0, np.nan), 0.0)
    mfv = pd.Series(mfm, index=df.index) * v
    adl = mfv.cumsum()
    df["co_mfv"] = mfv
    df["co_adl"] = adl
    df["co_cho"] = B.ema(adl, 3) - B.ema(adl, 10)
    df["sma50"] = B.sma(df["c"], 50)
    return df
