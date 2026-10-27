"""Nison doji reversal detector.

Doji: |C - O| <= 10% of the bar's range (and range > 0). Location
is the signal: the doji must print at the 10-bar extreme (lowest
low for longs, highest high for shorts) after a 3-bar trend in the
opposite direction. A doji mid-range is indecision, not a signal,
and is ignored. Columns: doji_dir (+1/-1/0), atr.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o, h, l, c = df["o"], df["h"], df["l"], df["c"]
    body = (c - o).abs()
    rng = h - l
    is_doji = (rng > 0) & (body <= 0.10 * rng)
    low_extreme = l <= l.rolling(10, min_periods=10).min()
    high_extreme = h >= h.rolling(10, min_periods=10).max()
    downtrend = c.shift(1) < c.shift(4)
    uptrend = c.shift(1) > c.shift(4)
    bull = is_doji & low_extreme & downtrend
    bear = is_doji & high_extreme & uptrend
    df["doji_dir"] = np.where(bull, 1, np.where(bear, -1, 0))
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
