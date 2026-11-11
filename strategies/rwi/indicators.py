"""Chande & Kroll Random Walk Index (RWI) indicators.

Tushar Chande & Stanley Kroll, "The New Technical Trader" (1994):
the Random Walk Index compares the current price range to the range
that would be expected from a random walk, using ATR as the yardstick
for one bar's typical movement.

    RWI-high[i] = (high[i] - low[i-14]) / ATR(14)[i]
    RWI-low[i]  = (high[i-14] - low[i]) / ATR(14)[i]

A reading above 1.0 means price has moved further in 14 bars than
a random walk would typically travel in one bar — a genuine trend
move rather than noise. All computation is causal: every value on
bar i uses only data through bar i's close.
"""

import pandas as pd

from strategies.base import atr

N = 14

INDICATOR_COLS = ["atr_14", "rwi_high", "rwi_low"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    a = atr(df["h"], df["l"], df["c"], N)
    df["atr_14"] = a
    df["rwi_high"] = (df["h"] - df["l"].shift(N)) / a
    df["rwi_low"] = (df["h"].shift(N) - df["l"]) / a
    return df
