"""Wyckoff spring/upthrust signals.

Entries on the shakeout with volume confirmation:
  long_entry:  spring and volume > 20-bar average
  short_entry: upthrust and volume > 20-bar average
Exits: the range objective is met (longs: close back at/above the range
top; shorts: close at/below the range bottom) or the opposite shakeout
fires.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = (df["spring"] & df["vol_ok"]).fillna(False)
    df["short_entry"] = (df["upthrust"] & df["vol_ok"]).fillna(False)
    df["long_exit"] = ((df["c"] >= df["range_high"]) | df["short_entry"]).fillna(False)
    df["short_exit"] = ((df["c"] <= df["range_low"]) | df["long_entry"]).fillna(False)
    return df
