"""Keltner + MACD signals: band breakout with MACD confirmation."""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = ((df["c"] > df["kc_upper"]) & (df["macd"] > df["macd_signal"])).astype(bool)
    df["short_entry"] = ((df["c"] < df["kc_lower"]) & (df["macd"] < df["macd_signal"])).astype(bool)
    df["long_exit"] = (df["c"] < df["kc_mid"]).astype(bool)
    df["short_exit"] = (df["c"] > df["kc_mid"]).astype(bool)
    return df
