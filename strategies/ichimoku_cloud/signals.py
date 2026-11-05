"""Ichimoku Cloud signals: Tenkan/Kijun cross + price above/below the cloud
+ green/red cloud ahead + Chikou confirmation.

Chikou check is computed directly as c > c.shift(26) (long) /
c < c.shift(26) (short) — the current close vs the close 26 bars ago.
B.ichimoku()'s 'chikou' column (c.shift(-26)) is NEVER used: it contains
future closes. Senkou spans are already shifted +26 by B.ichimoku(), so the
cloud value at bar i is the one computed 26 bars ago — correct to use."""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    above_cloud = (df["c"] > df["senkou_a"]) & (df["c"] > df["senkou_b"])
    below_cloud = (df["c"] < df["senkou_a"]) & (df["c"] < df["senkou_b"])
    cloud_green = df["senkou_a"] > df["senkou_b"]
    cloud_red = df["senkou_a"] < df["senkou_b"]
    # Chikou confirmation, lookahead-free: current close vs close 26 bars ago.
    chikou_long = df["c"] > df["c"].shift(26)
    chikou_short = df["c"] < df["c"].shift(26)
    df["long_entry"] = (
        B.crossed_above(df["tenkan"], df["kijun"])
        & above_cloud
        & cloud_green
        & chikou_long
    ).astype(bool)
    df["short_entry"] = (
        B.crossed_below(df["tenkan"], df["kijun"])
        & below_cloud
        & cloud_red
        & chikou_short
    ).astype(bool)
    df["long_exit"] = (
        B.crossed_below(df["tenkan"], df["kijun"])
        | (df["c"] < df["senkou_a"])
        | (df["c"] < df["senkou_b"])
    ).astype(bool)
    df["short_exit"] = (
        B.crossed_above(df["tenkan"], df["kijun"])
        | (df["c"] > df["senkou_a"])
        | (df["c"] > df["senkou_b"])
    ).astype(bool)
    return df
