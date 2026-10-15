"""Ease of Movement signals (Arms).

Entries on the smoothed EMV crossing the zero line — price starting to
move "easily" in a direction is the Arms trend-change read:
  long_entry:  EMV(14) crosses above 0
  short_entry: EMV(14) crosses below 0
Exits: the opposite cross.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    emv = df["emv"]
    prev = emv.shift(1)
    df["long_entry"] = ((emv > 0) & (prev <= 0)).fillna(False)
    df["short_entry"] = ((emv < 0) & (prev >= 0)).fillna(False)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
