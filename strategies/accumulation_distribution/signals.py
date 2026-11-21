"""Accumulation/Distribution Line signals.

Long entry:  AD crosses up through its SMA(20) (transition only).
Short entry: AD crosses down through its SMA(20) (transition only).
Long exit:   AD crosses down through SMA(20).
Short exit:  AD crosses up through SMA(20).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ad = df["ad"]
    sma = df["ad_sma"]
    prev_ad = ad.shift(1)
    prev_sma = sma.shift(1)
    cross_up = (ad > sma) & (prev_ad <= prev_sma)
    cross_down = (ad < sma) & (prev_ad >= prev_sma)
    df["long_entry"] = cross_up.fillna(False).astype(bool)
    df["short_entry"] = cross_down.fillna(False).astype(bool)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
