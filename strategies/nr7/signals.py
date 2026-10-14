"""NR7 signals.

On bar i, look at bar i-1: if is_nr7[i-1] is set, the current bar breaks
the NR7 bar's extremes:
    long_entry  = c[i] > h[i-1]     (prior bar was NR7)
    short_entry = c[i] < l[i-1]     (prior bar was NR7)
First break wins: both cannot trigger on one bar because a single close
cannot be simultaneously above the NR7 high and below the NR7 low.

Exits: reverse on the opposite break — a long exits when the short-entry
condition fires (the NR7 low breaks), and vice versa. Crabel's original
setup stops at the opposite extreme / exits at close; the ATR stop and the
max-hold bar cap in risk.py cover the rest.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_nr7 = df["is_nr7"].shift(1).fillna(False)
    prev_high = df["nr7_high"].shift(1)
    prev_low = df["nr7_low"].shift(1)
    df["long_entry"] = (prev_nr7 & (df["c"] > prev_high)).fillna(False)
    df["short_entry"] = (prev_nr7 & (df["c"] < prev_low)).fillna(False)
    # reverse exits: the opposite extreme's break closes the position
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
