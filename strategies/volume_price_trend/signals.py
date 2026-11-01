"""PVT / average cross signals.

    long_entry  -- PVT crosses above its 20-bar average
    short_entry -- PVT crosses below its 20-bar average
    long_exit   -- PVT crosses below its 20-bar average (opposite cross)
    short_exit  -- PVT crosses above its 20-bar average (opposite cross)

Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["vpt"], df["vpt_avg"]).fillna(False)
    down = B.crossed_below(df["vpt"], df["vpt_avg"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
