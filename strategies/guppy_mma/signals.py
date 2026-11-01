"""Guppy MMA signals.

    long_entry  -- short-group mean crosses above long-group mean
    short_entry -- short-group mean crosses below long-group mean
    long_exit   -- short-group mean crosses below long-group mean
    short_exit  -- short-group mean crosses above long-group mean

State machine: entries only while flat; an opposite cross exits and
may re-enter the other side on the same bar. Boolean columns, no NaN,
no lookahead.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["short_mean"], df["long_mean"]).fillna(False)
    down = B.crossed_below(df["short_mean"], df["long_mean"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
