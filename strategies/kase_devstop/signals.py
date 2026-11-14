"""Kase DevStop flip signals.

The DevStop line is both the entry trigger and the exit: a close
through the active stop flips the state, and that flip is the signal.

    long_entry  = devstop_dir flips -1 -> +1 (close above short stop)
    short_entry = devstop_dir flips +1 -> -1 (close below long stop)
    long_exit   = flip to short (same bar as short_entry)
    short_exit  = flip to long  (same bar as long_entry)

The harness exits the open position at the next bar's open and can
re-enter the other way on the same bar, so a flip is a clean reversal.
Signal columns are boolean, no NaN, no lookahead.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = df["devstop_dir"]
    prev = d.shift(1)
    flip_up = ((d == 1) & (prev == -1)).fillna(False).astype(bool)
    flip_dn = ((d == -1) & (prev == 1)).fillna(False).astype(bool)
    df["long_entry"] = flip_up
    df["short_entry"] = flip_dn
    df["long_exit"] = flip_dn
    df["short_exit"] = flip_up
    return df
