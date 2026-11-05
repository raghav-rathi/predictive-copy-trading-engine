"""Turtle Trading signals: System 1 (20-bar entry / 10-bar exit) + System 2
(55-bar entry / 20-bar exit), combined — either system firing enters.

Channels are shifted by 1 so the close is compared to the PRIOR bar's
channel values: a close can never exceed its own bar's channel.
The combined exit uses the tighter 10-bar channel for both systems
(the 20-bar exit is subsumed: the 10-bar low is always >= the 20-bar low,
so a close below the 10-bar low exits first)."""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hi20 = df["donchian_high_20"].shift(1)
    lo20 = df["donchian_low_20"].shift(1)
    hi55 = df["donchian_high_55"].shift(1)
    lo55 = df["donchian_low_55"].shift(1)
    lo10 = df["donchian_low_10"].shift(1)
    hi10 = df["donchian_high_10"].shift(1)
    df["long_entry"] = ((df["c"] > hi20) | (df["c"] > hi55)).astype(bool)
    df["short_entry"] = ((df["c"] < lo20) | (df["c"] < lo55)).astype(bool)
    df["long_exit"] = (df["c"] < lo10).astype(bool)
    df["short_exit"] = (df["c"] > hi10).astype(bool)
    return df
