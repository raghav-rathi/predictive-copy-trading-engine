"""Kijun-sen cross signals.

    long_entry  -- close crosses above Kijun-sen
    short_entry -- close crosses below Kijun-sen
    long_exit   -- close crosses below Kijun-sen
    short_exit  -- close crosses above Kijun-sen
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["c"], df["kijun"]).fillna(False)
    down = B.crossed_below(df["c"], df["kijun"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
