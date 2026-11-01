"""CPR breakout signals.

    long_entry  -- close crosses above the prior day's TC
    short_entry -- close crosses below the prior day's BC
    long_exit   -- close crosses below the prior day's Pivot
    short_exit  -- close crosses above the prior day's Pivot

Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    le = B.crossed_above(df["c"], df["cpr_tc"]).fillna(False)
    se = B.crossed_below(df["c"], df["cpr_bc"]).fillna(False)
    lx = B.crossed_below(df["c"], df["cpr_pivot"]).fillna(False)
    sx = B.crossed_above(df["c"], df["cpr_pivot"]).fillna(False)
    df["long_entry"] = le.astype(bool)
    df["short_entry"] = se.astype(bool)
    df["long_exit"] = lx.astype(bool)
    df["short_exit"] = sx.astype(bool)
    return df
