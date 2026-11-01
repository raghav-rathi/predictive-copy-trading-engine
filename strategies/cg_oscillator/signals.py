"""CG / trigger-line cross signals.

    long_entry  -- CG crosses above its trigger line
    short_entry -- CG crosses below its trigger line
    long_exit   -- CG crosses below its trigger line (opposite cross)
    short_exit  -- CG crosses above its trigger line (opposite cross)

Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["cg"], df["cg_trigger"]).fillna(False)
    down = B.crossed_below(df["cg"], df["cg_trigger"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
