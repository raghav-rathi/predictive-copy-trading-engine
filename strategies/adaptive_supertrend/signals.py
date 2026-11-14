"""Adaptive Supertrend flip signals.

    long_entry  = supertrend_dir flips -1 -> +1
    short_entry = supertrend_dir flips +1 -> -1
    long_exit   = flip to down (same bar as short_entry)
    short_exit  = flip to up   (same bar as long_entry)

A flip is a close through the opposite final band, so the exit is the
same event as the opposite entry -- the harness exits the open
position at the next bar's open and can re-enter the other way on the
same bar. Signal columns are boolean, no NaN, no lookahead.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = df["supertrend_dir"]
    prev = d.shift(1)
    flip_up = ((d == 1) & (prev == -1)).fillna(False).astype(bool)
    flip_dn = ((d == -1) & (prev == 1)).fillna(False).astype(bool)
    df["long_entry"] = flip_up
    df["short_entry"] = flip_dn
    df["long_exit"] = flip_dn
    df["short_exit"] = flip_up
    return df
