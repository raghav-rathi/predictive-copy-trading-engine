"""ZigZag swing breakout signals.

    long_entry  -- close crosses above the last confirmed swing high
    short_entry -- close crosses below the last confirmed swing low
    long_exit   -- close crosses below the last confirmed swing low
    short_exit  -- close crosses above the last confirmed swing high
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["c"], df["swing_high"]).fillna(False)
    down = B.crossed_below(df["c"], df["swing_low"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
