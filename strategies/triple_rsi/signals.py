"""Triple RSI signals.

Long entry:  all three RSIs (7, 14, 21) above 55, triggered on the
             bar the last of the three crosses above 55 — i.e. the
             first bar on which all three are above 55 after at
             least one was at or below 55.
Short entry: all three RSIs below 45, triggered on the bar the
             last of the three crosses below 45.
Long exit:   any RSI crosses below 50.
Short exit:  any RSI crosses above 50.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def _crossed_below_level(s, level):
    return B.crossed_below(s, level).fillna(False).astype(bool)


def _crossed_above_level(s, level):
    return B.crossed_above(s, level).fillna(False).astype(bool)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsi_cols = ["rsi7", "rsi14", "rsi21"]
    all_above_55 = pd.Series(True, index=df.index)
    all_below_45 = pd.Series(True, index=df.index)
    for col in rsi_cols:
        all_above_55 = all_above_55 & (df[col] > 55).fillna(False)
        all_below_45 = all_below_45 & (df[col] < 45).fillna(False)
    # Entry fires only on a genuine transition: the previous bar must
    # exist and must NOT have had all three on the same side. (A bare
    # shift(1).fillna(False) would fire spuriously on bar 0, where
    # there is no previous bar to cross from.)
    prev_above = all_above_55.shift(1)
    prev_below = all_below_45.shift(1)
    long_entry = all_above_55 & (prev_above == False)
    short_entry = all_below_45 & (prev_below == False)
    long_exit = pd.Series(False, index=df.index)
    short_exit = pd.Series(False, index=df.index)
    for col in rsi_cols:
        long_exit = long_exit | _crossed_below_level(df[col], 50)
        short_exit = short_exit | _crossed_above_level(df[col], 50)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
