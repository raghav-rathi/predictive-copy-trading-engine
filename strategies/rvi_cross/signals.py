"""RVI / signal-line cross signals.

    long_entry  -- RVI crosses above its signal line
    short_entry -- RVI crosses below its signal line
    long_exit   -- RVI crosses below its signal line (opposite cross)
    short_exit  -- RVI crosses above its signal line (opposite cross)

Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["rvi"], df["rvi_signal"]).fillna(False)
    down = B.crossed_below(df["rvi"], df["rvi_signal"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
