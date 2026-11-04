"""PVO signals: signal-line crosses filtered by SMA(50) price trend."""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["pvo"], df["pvo_signal"]).fillna(False)
    down = B.crossed_below(df["pvo"], df["pvo_signal"]).fillna(False)
    df["long_entry"] = (up & (df["c"] > df["sma50"])).astype(bool)
    df["short_entry"] = (down & (df["c"] < df["sma50"])).astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
