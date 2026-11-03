"""Cutler RSI signals.

Cutler's RSI (14): Wilder's RSI with simple moving averages of gains/losses instead of Wilder smoothing. Long on cross above 30 from oversold, short on cross below 70 from overbought; exits at the opposite extreme.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_e = B.crossed_above(df["rsi"], 30).fillna(False)
    short_e = B.crossed_below(df["rsi"], 70).fillna(False)
    df["long_entry"] = long_e.astype(bool)
    df["short_entry"] = short_e.astype(bool)
    df["long_exit"] = B.crossed_above(df["rsi"], 70).fillna(False).astype(bool)
    df["short_exit"] = B.crossed_below(df["rsi"], 30).fillna(False).astype(bool)
    return df
