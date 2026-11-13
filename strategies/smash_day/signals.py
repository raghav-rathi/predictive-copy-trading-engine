"""Smash Day signals (Larry Williams, 1999).

Long entry:  a smash setup is active and the 1h close crosses above the
             inside day's high (the breakout of the contraction range).
Short entry: a smash setup is active and the 1h close crosses below the
             inside day's low.
Long exit:   close crosses back below the inside day's low (failed break).
Short exit:  close crosses back above the inside day's high.

The harness risk layer's 2xATR stop / 2.5xATR trail and 120-bar max hold
also apply. Signal columns are boolean, no NaN, no lookahead (the
harness executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    active = df["setup_active"].fillna(False).astype(bool)
    ih = df["inside_high"]
    il = df["inside_low"]
    long_entry = B.crossed_above(df["c"], ih) & active
    short_entry = B.crossed_below(df["c"], il) & active
    long_exit = B.crossed_below(df["c"], il)
    short_exit = B.crossed_above(df["c"], ih)
    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = long_exit.fillna(False).astype(bool)
    df["short_exit"] = short_exit.fillna(False).astype(bool)
    return df
