"""Donchian channel signals: 20-bar breakout, exit back through the midline.

The close is compared to the PRIOR bar's channel values (shifted by 1):
a close can never exceed its own bar's channel."""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hi = df["donchian_high_20"].shift(1)
    lo = df["donchian_low_20"].shift(1)
    mid = df["donchian_mid_20"].shift(1)
    df["long_entry"] = (df["c"] > hi).astype(bool)
    df["short_entry"] = (df["c"] < lo).astype(bool)
    df["long_exit"] = (df["c"] < mid).astype(bool)
    df["short_exit"] = (df["c"] > mid).astype(bool)
    return df
