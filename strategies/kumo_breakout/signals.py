"""Kumo breakout signals.

    long_entry  -- close crosses above the cloud top
    short_entry -- close crosses below the cloud bottom
    long_exit   -- close crosses back below the cloud top (re-enters cloud)
    short_exit  -- close crosses back above the cloud bottom
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["c"], df["cloud_top"]).fillna(False)
    down = B.crossed_below(df["c"], df["cloud_bottom"]).fillna(False)
    back_in_down = B.crossed_below(df["c"], df["cloud_top"]).fillna(False)
    back_in_up = B.crossed_above(df["c"], df["cloud_bottom"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = back_in_down.astype(bool)
    df["short_exit"] = back_in_up.astype(bool)
    return df
