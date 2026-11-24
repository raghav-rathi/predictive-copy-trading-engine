"""Spinning top reversal signals (Steve Nison).

A spinning top is indecision — long wicks both ways, small
body. At a swing extreme it reads as exhaustion of the move
into that extreme:

Long: a spinning top appears AND its low reaches the lowest
low of the prior 20 bars (at a swing low).
Short: a spinning top appears AND its high reaches the highest
high of the prior 20 bars (at a swing high).

Exit on the opposite signal — a spinning top at the opposite
extreme says the reversal itself is exhausted. Signal columns
are boolean, no NaN, no lookahead (execution at next-bar open
is handled by the harness).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    top = df["is_spinning_top"].fillna(False)
    long_entry = (top & (df["l"] <= df["swing_low"])).fillna(False)
    short_entry = (top & (df["h"] >= df["swing_high"])).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
