"""Camarilla Pivot Breakout signals.

Long entry:  close crosses above prior-day R3 (transition only).
Short entry: close crosses below prior-day S3 (transition only).
Long exit:   close crosses back below R3.
Short exit:  close crosses back above S3.

Crosses are judged against the CURRENT bar's level for both the
current and the previous close: the level only changes at a UTC-day
boundary, and comparing the previous close to the previous bar's
(stale) level would let a level jump alone fire a signal with no
price move. NaN levels (first UTC day) never fire.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    prev_c = c.shift(1)
    r3 = df["r3"]
    s3 = df["s3"]
    cross_up_r3 = (c > r3) & (prev_c <= r3)
    cross_down_s3 = (c < s3) & (prev_c >= s3)
    cross_down_r3 = (c < r3) & (prev_c >= r3)
    cross_up_s3 = (c > s3) & (prev_c <= s3)
    df["long_entry"] = cross_up_r3.fillna(False).astype(bool)
    df["short_entry"] = cross_down_s3.fillna(False).astype(bool)
    df["long_exit"] = cross_down_r3.fillna(False).astype(bool)
    df["short_exit"] = cross_up_s3.fillna(False).astype(bool)
    return df
