"""Demark-style trendline breakout signals.

Long entry:  close crosses above the downtrend line (line through
             the last two confirmed swing highs).
Short entry: close crosses below the uptrend line (line through
             the last two confirmed swing lows).
Long exit:   close crosses below the uptrend line.
Short exit:  close crosses above the downtrend line.

"Breaks" is read as a cross (previous close on the old side of
the line, current close on the new side), not as merely sitting
on one side of the line — otherwise a position would re-enter on
every bar while price stays beyond a line. A cross also cannot
fire on the bar a line first appears (previous-bar comparison
against a NaN line is False).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    down = df["downtrend_line"]
    up = df["uptrend_line"]
    long_entry = B.crossed_above(c, down).fillna(False).astype(bool)
    short_entry = B.crossed_below(c, up).fillna(False).astype(bool)
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = short_entry
    df["short_exit"] = long_entry
    return df
