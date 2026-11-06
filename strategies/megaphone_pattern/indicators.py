"""Megaphone Pattern indicators: ATR(14) + 5-bar zigzag swing pivots.

A swing high is a bar whose high is the max of the 5-bar window centred
on it and strictly above both neighbouring highs; a swing low is the
mirror. The pivot value is only published 2 bars after the extreme bar
(shift(2)), so no signal can ever use a pivot before it is confirmed.
"""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["atr14", "swing_high", "swing_low"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    h = df["h"]
    l = df["l"]
    roll_max = h.rolling(5, center=True, min_periods=5).max()
    roll_min = l.rolling(5, center=True, min_periods=5).min()
    is_high = (h == roll_max) & (h > h.shift(1)) & (h > h.shift(-1))
    is_low = (l == roll_min) & (l < l.shift(1)) & (l < l.shift(-1))
    df["swing_high"] = h.where(is_high).shift(2)
    df["swing_low"] = l.where(is_low).shift(2)
    return df
