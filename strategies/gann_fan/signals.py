"""Gann fan signals.

    long_entry  -- close crosses above the rising 1x1 fan
    short_entry -- close crosses below the falling 1x1 fan
    long_exit   -- close crosses below the rising fan
    short_exit  -- close crosses above the falling fan
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["c"], df["fan_up"]).fillna(False)
    down = B.crossed_below(df["c"], df["fan_down"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
