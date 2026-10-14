"""Mass Index indicators (Donald Dorsey, Stocks & Commodities, June 1992).

MI = sum over 25 bars of EMA(High-Low, 9) / EMA(EMA(High-Low, 9), 9).
A "reversal bulge" = MI rises above 27 then falls back below 26.5.

OUR EXTENSION (not in Dorsey's publication — the published indicator is
directionless): on bulge completion, go long if close < SMA(20) (price weak
into the volatility expansion => snap-back up) and short if close > SMA(20).
This directional overlay is marked as ours here and in BACKTEST.md.
"""

import numpy as np
import pandas as pd

from strategies import base as B

RANGE_EMA = 9
MI_SUM = 25
BULGE_HIGH = 27.0
BULGE_LOW = 26.5
SMA_LEN = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rng = df["h"] - df["l"]
    e1 = B.ema(rng, RANGE_EMA)
    e2 = B.ema(e1, RANGE_EMA)
    df["mi"] = (e1 / e2).rolling(MI_SUM, min_periods=MI_SUM).sum()
    df["sma20"] = B.sma(df["c"], SMA_LEN)

    mi = df["mi"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    sma = df["sma20"].to_numpy(dtype=float)
    n = len(df)
    bulge_long = np.zeros(n, dtype=bool)
    bulge_short = np.zeros(n, dtype=bool)
    armed = False
    for i in range(n):
        v = mi[i]
        if np.isnan(v):
            continue
        if not armed and v > BULGE_HIGH:
            armed = True
        elif armed and v < BULGE_LOW:
            armed = False
            if c[i] < sma[i]:
                bulge_long[i] = True
            elif c[i] > sma[i]:
                bulge_short[i] = True
            # c == sma20 exactly: no directional call
    df["bulge_long"] = bulge_long
    df["bulge_short"] = bulge_short
    return df
