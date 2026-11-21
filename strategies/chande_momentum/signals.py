"""Chande Momentum Oscillator signals.

Long entry:  CMO crosses up through -50 (transition only).
Short entry: CMO crosses down through +50 (transition only).
Long exit:   CMO crosses down through +50 (i.e. the short entry).
Short exit:  CMO crosses up through -50 (i.e. the long entry).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cmo = df["cmo"]
    prev = cmo.shift(1)
    cross_up_m50 = (cmo > -50) & (prev <= -50)
    cross_down_p50 = (cmo < 50) & (prev >= 50)
    df["long_entry"] = cross_up_m50.fillna(False).astype(bool)
    df["short_entry"] = cross_down_p50.fillna(False).astype(bool)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
