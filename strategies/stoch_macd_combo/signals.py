"""Stochastic + MACD signals: oversold/overbought %K crosses with MACD confirmation."""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["stoch_k"], df["stoch_d"]).fillna(False)
    down = B.crossed_below(df["stoch_k"], df["stoch_d"]).fillna(False)
    df["long_entry"] = (up & (df["stoch_k"] < 30) & (df["macd"] > df["macd_signal"])).astype(bool)
    df["short_entry"] = (down & (df["stoch_k"] > 70) & (df["macd"] < df["macd_signal"])).astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
