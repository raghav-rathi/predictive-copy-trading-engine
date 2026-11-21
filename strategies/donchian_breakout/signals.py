"""Donchian Channel Breakout signals.

Long entry:  close > prior-20-bar high (transition only — the
               previous bar's close was NOT above the then-current
               upper channel).
Short entry: close < prior-20-bar low (transition only).
Long exit:   close < prior-20-bar low, OR close < lowest low of
               the prior 10 bars (Turtle 10-bar exit).
Short exit:  mirror of the long exit.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    up = df["dc_upper"]
    lo = df["dc_lower"]
    prev_c = c.shift(1)
    prev_up = up.shift(1)
    prev_lo = lo.shift(1)
    df["long_entry"] = (
        (c > up) & (prev_c <= prev_up)).fillna(False).astype(bool)
    df["short_entry"] = (
        (c < lo) & (prev_c >= prev_lo)).fillna(False).astype(bool)
    df["long_exit"] = (
        (c < lo) | (c < df["exit_low"])).fillna(False).astype(bool)
    df["short_exit"] = (
        (c > up) | (c > df["exit_high"])).fillna(False).astype(bool)
    return df
