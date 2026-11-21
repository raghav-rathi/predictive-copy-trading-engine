"""Relative Vigor Index signals.

Long entry:  RVI crosses up through signal (transition only).
Short entry: RVI crosses down through signal (transition only).
Long exit:   RVI crosses down through signal.
Short exit:  RVI crosses up through signal.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rvi = df["rvi"]
    sig = df["rvi_signal"]
    prev_rvi = rvi.shift(1)
    prev_sig = sig.shift(1)
    cross_up = ((rvi > sig) & (prev_rvi <= prev_sig)).fillna(False).astype(bool)
    cross_down = ((rvi < sig) & (prev_rvi >= prev_sig)).fillna(False).astype(bool)
    df["long_entry"] = cross_up
    df["short_entry"] = cross_down
    df["long_exit"] = cross_down
    df["short_exit"] = cross_up
    return df
