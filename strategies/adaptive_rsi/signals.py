"""Adaptive RSI signals.

    long_entry  -- adaptive RSI crosses above 30 (oversold recovery)
    short_entry -- adaptive RSI crosses below 70 (overbought failure)
    long_exit   -- adaptive RSI crosses below 50
    short_exit  -- adaptive RSI crosses above 50
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up30 = B.crossed_above(df["arsi"], 30).fillna(False)
    down70 = B.crossed_below(df["arsi"], 70).fillna(False)
    down50 = B.crossed_below(df["arsi"], 50).fillna(False)
    up50 = B.crossed_above(df["arsi"], 50).fillna(False)
    df["long_entry"] = up30.astype(bool)
    df["short_entry"] = down70.astype(bool)
    df["long_exit"] = down50.astype(bool)
    df["short_exit"] = up50.astype(bool)
    return df
