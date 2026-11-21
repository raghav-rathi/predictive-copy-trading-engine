"""Accumulation/Distribution Line indicators.

Marc Chaikin. For each bar:

    MFM = ((C - L) - (H - C)) / (H - L)   (money flow multiplier)
    MFV = MFM * v                          (money flow volume)
    AD  = cumulative sum of MFV            (accumulation/distribution line)

H == L is guarded to MFM = 0 (that bar contributes nothing).
The signal line is SMA(20) of AD.

Columns:
    mfm -- money flow multiplier, in [-1, +1]
    mfv -- money flow volume
    ad -- accumulation/distribution line (cumulative)
    ad_sma -- SMA(20) of AD
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only. The SMA is trailing (include bar i, exclude later bars).
"""

import numpy as np
import pandas as pd

from strategies import base as B

SMA_N = 20
ATR_N = 14


def add_indicators(df: pd.DataFrame, sma_n: int = SMA_N,
                   atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    h = df["h"]
    l = df["l"]
    c = df["c"]
    v = df["v"]

    rng = h - l
    mfm = np.where(
        rng == 0, 0.0, ((c - l) - (h - c)) / rng.replace(0, np.nan)
    )
    df["mfm"] = pd.Series(mfm, index=df.index, dtype=float)
    df["mfv"] = df["mfm"] * v
    df["ad"] = df["mfv"].cumsum()
    df["ad_sma"] = B.sma(df["ad"], sma_n)
    df["atr"] = B.atr(h, l, c, atr_n)
    return df
