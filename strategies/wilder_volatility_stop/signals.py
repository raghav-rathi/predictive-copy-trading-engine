"""Wilder Volatility Stop signals: entries are trend flips, exits are the
opposite flip. A flip is detected from the trend column (computed from
data through the current bar's close), so the signal on bar i fires on a
close through the stop fixed at bar i-1."""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_trend = df["vol_trend"].shift(1)
    flip_up = (df["vol_trend"] == 1.0) & (prev_trend == -1.0)
    flip_down = (df["vol_trend"] == -1.0) & (prev_trend == 1.0)
    df["long_entry"] = flip_up.fillna(False).astype(bool)
    df["short_entry"] = flip_down.fillna(False).astype(bool)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
