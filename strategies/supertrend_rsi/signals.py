"""Supertrend + RSI signals.

Long entry:  price (close) above the Supertrend line AND RSI
             crosses above 50.
Short entry: price (close) below the Supertrend line AND RSI
             crosses below 50.
Long exit:   Supertrend flips bearish (direction +1 -> -1, i.e.
             the close falls below the line).
Short exit:  Supertrend flips bullish (direction -1 -> +1).

The RSI cross is a genuine cross (previous RSI on the old side
of 50, current RSI on the new side), so a long entry needs a
fresh RSI turn up through 50 while price is already above the
line — not merely RSI sitting above 50. The exits use the
direction flip rather than a raw close-vs-line cross, because
the Supertrend line jumps to the opposite band on the flip bar
and a raw cross against the post-flip line would miss the flip.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    st = df["supertrend"]
    direction = df["supertrend_dir"]
    rsi = df["rsi"]
    long_entry = ((c > st) & B.crossed_above(rsi, 50)).fillna(False).astype(bool)
    short_entry = ((c < st) & B.crossed_below(rsi, 50)).fillna(False).astype(bool)
    # Direction flip: NaN comparisons are False, so no exit fires
    # before the first valid Supertrend bar.
    long_exit = ((direction == -1) & (direction.shift(1) == 1)).fillna(False).astype(bool)
    short_exit = ((direction == 1) & (direction.shift(1) == -1)).fillna(False).astype(bool)
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
