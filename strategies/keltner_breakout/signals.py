"""Keltner breakout signals.

    long_entry  -- close crosses above the upper band
    short_entry -- close crosses below the lower band
    long_exit   -- close crosses back below the midline
    short_exit  -- close crosses back above the midline
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["c"], df["kc_upper"]).fillna(False)
    down = B.crossed_below(df["c"], df["kc_lower"]).fillna(False)
    to_mid_down = B.crossed_below(df["c"], df["kc_mid"]).fillna(False)
    to_mid_up = B.crossed_above(df["c"], df["kc_mid"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = to_mid_down.astype(bool)
    df["short_exit"] = to_mid_up.astype(bool)
    return df
