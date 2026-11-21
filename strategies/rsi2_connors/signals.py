"""Connors RSI signals.

Long entry:  CRSI crosses below 10 (transition only).
Short entry: CRSI crosses above 90 (transition only).
Long exit:   CRSI crosses above 50.
Short exit:  CRSI crosses below 50.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame, long_below: float = 10.0,
                short_above: float = 90.0,
                exit_mid: float = 50.0) -> pd.DataFrame:
    df = df.copy()
    crsi = df["crsi"]
    prev = crsi.shift(1)
    df["long_entry"] = (
        (crsi < long_below) & (prev >= long_below)
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        (crsi > short_above) & (prev <= short_above)
    ).fillna(False).astype(bool)
    df["long_exit"] = (
        (crsi > exit_mid) & (prev <= exit_mid)
    ).fillna(False).astype(bool)
    df["short_exit"] = (
        (crsi < exit_mid) & (prev >= exit_mid)
    ).fillna(False).astype(bool)
    return df
