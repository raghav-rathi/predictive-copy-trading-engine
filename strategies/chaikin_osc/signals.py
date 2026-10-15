"""Chaikin Oscillator signals.

Entries on the oscillator crossing the zero line — the textbook Chaikin
money-flow momentum flip:
  long_entry:  CHO crosses above 0 (accumulation momentum)
  short_entry: CHO crosses below 0 (distribution momentum)
Exits: the opposite cross.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cho = df["chaikin_osc"]
    prev = cho.shift(1)
    df["long_entry"] = ((cho > 0) & (prev <= 0)).fillna(False)
    df["short_entry"] = ((cho < 0) & (prev >= 0)).fillna(False)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
