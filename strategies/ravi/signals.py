"""RAVI signals (Chande's reference lines).

    long_entry  -- RAVI crosses above +0.3 (uptrend starts)
    short_entry -- RAVI crosses below -0.3 (downtrend starts)
    long_exit   -- RAVI crosses back below 0 (trend ends)
    short_exit  -- RAVI crosses back above 0 (trend ends)
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["ravi"], 0.3).fillna(False)
    down = B.crossed_below(df["ravi"], -0.3).fillna(False)
    end_up = B.crossed_below(df["ravi"], 0.0).fillna(False)
    end_down = B.crossed_above(df["ravi"], 0.0).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = end_up.astype(bool)
    df["short_exit"] = end_down.astype(bool)
    return df
