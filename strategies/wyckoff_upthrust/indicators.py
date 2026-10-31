"""Wyckoff upthrust indicators.

Trading range from PRIOR bars only (strictly causal): the range high
and low on bar i are the max high / min low over the 20 bars before
bar i, i.e. the 20-bar rolling extremes shifted by 1. Bar i's own
high/low never enter its own range, so a breakout bar is judged
against a range it did not help form.

    range_high = rolling max(high, 20) shifted by 1
    range_low  = rolling min(low, 20) shifted by 1
    upthrust   = (high > range_high) AND (close < range_high)
                 AND (close > range_low)
                 -- price breaks above the range, then closes back
                    inside it: the breakout failed.

Columns:
    range_high, range_low -- prior-20-bar range extremes (NaN first 20 bars)
    upthrust              -- boolean upthrust bar flag
    atr                   -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

WINDOW = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["range_high"] = df["h"].rolling(WINDOW, min_periods=WINDOW).max().shift(1)
    df["range_low"] = df["l"].rolling(WINDOW, min_periods=WINDOW).min().shift(1)
    rh, rl = df["range_high"], df["range_low"]
    df["upthrust"] = (
        (df["h"] > rh) & (df["c"] < rh) & (df["c"] > rl)
    ).fillna(False)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
