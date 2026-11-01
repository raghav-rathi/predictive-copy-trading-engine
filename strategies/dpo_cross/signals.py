"""DPO zero-cross signals.

    long_entry  -- DPO crosses above zero
    short_entry -- DPO crosses below zero
    long_exit   -- DPO crosses below zero (opposite cross)
    short_exit  -- DPO crosses above zero (opposite cross)

Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["dpo"], 0.0).fillna(False)
    down = B.crossed_below(df["dpo"], 0.0).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
