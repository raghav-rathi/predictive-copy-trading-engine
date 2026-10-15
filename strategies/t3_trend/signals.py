"""Tillson T3 signals.

Traded like any moving-average pair (the T3's documented use):
  long_entry:  T3(5) crosses above T3(15)
  short_entry: T3(5) crosses below T3(15)
Exits: the opposite cross.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast, slow = df["t3_fast"], df["t3_slow"]
    df["long_entry"] = B.crossed_above(fast, slow).fillna(False)
    df["short_entry"] = B.crossed_below(fast, slow).fillna(False)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
