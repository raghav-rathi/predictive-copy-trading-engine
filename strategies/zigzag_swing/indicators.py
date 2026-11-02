"""ZigZag swing breakout indicators.

A causal pivot tracker with a 5% deviation: while tracking up, a
5% fall from the running extreme confirms that extreme as a swing
high and flips tracking down (and vice versa). Only confirmed
pivots are traded — the current unconfirmed extreme is never a
level, so there is no repainting.

Columns:
    swing_high, swing_low (last confirmed pivots, NaN until first),
    atr
"""

import numpy as np
import pandas as pd

from strategies import base as B

DEVIATION = 0.05


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy()
    n = len(df)
    swing_high = np.full(n, np.nan)
    swing_low = np.full(n, np.nan)
    trend = 1
    extreme = c[0]
    last_high = np.nan
    last_low = np.nan
    for i in range(1, n):
        if trend == 1:
            if c[i] > extreme:
                extreme = c[i]
            elif c[i] < extreme * (1 - DEVIATION):
                last_high = extreme
                trend = -1
                extreme = c[i]
        else:
            if c[i] < extreme:
                extreme = c[i]
            elif c[i] > extreme * (1 + DEVIATION):
                last_low = extreme
                trend = 1
                extreme = c[i]
        swing_high[i] = last_high
        swing_low[i] = last_low
    df["swing_high"] = swing_high
    df["swing_low"] = swing_low
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
