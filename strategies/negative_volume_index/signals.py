"""NVI / EMA cross signals.

    long_entry  -- NVI crosses above its 255-bar EMA
    short_entry -- NVI crosses below its 255-bar EMA
    long_exit   -- NVI crosses below its 255-bar EMA (opposite cross)
    short_exit  -- NVI crosses above its 255-bar EMA (opposite cross)

Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["nvi"], df["nvi_ema"]).fillna(False)
    down = B.crossed_below(df["nvi"], df["nvi_ema"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
