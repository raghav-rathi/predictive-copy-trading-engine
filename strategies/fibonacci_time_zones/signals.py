"""Fibonacci time zones signals.

Long entry:  inside a Fib time-zone window, after a swing-low
             anchor in an uptrend (close > EMA(50)), a pullback
             close below EMA(20) followed by a close back above
             EMA(20) (long_trigger).
Short entry: the mirror — inside a zone window, after a swing-high
             anchor in a downtrend (close < EMA(50)), a rally
             close above EMA(20) followed by a close back below
             EMA(20) (short_trigger).
Long exit:   an opposite short signal OR a close below the most
             recent confirmed swing low (the anchor low).
Short exit:  an opposite long signal OR a close above the most
             recent confirmed swing high (the anchor high).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_trig = df["long_trigger"].fillna(False).astype(bool)
    short_trig = df["short_trigger"].fillna(False).astype(bool)
    df["long_entry"] = long_trig
    df["short_entry"] = short_trig
    df["long_exit"] = (short_trig | (df["c"] < df["anchor_low"])).fillna(False).astype(bool)
    df["short_exit"] = (long_trig | (df["c"] > df["anchor_high"])).fillna(False).astype(bool)
    return df
