"""Renko trend signals — trade the brick reversals:
  long_entry:  renko direction flips from -1 to +1 (up-brick after downs)
  short_entry: renko direction flips from +1 to -1
Exits: the opposite flip. Continuation bricks hold the position.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = df["renko_dir"]
    prev = d.shift(1).fillna(0)
    df["long_entry"] = ((d == 1) & (prev == -1)).fillna(False)
    df["short_entry"] = ((d == -1) & (prev == 1)).fillna(False)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
