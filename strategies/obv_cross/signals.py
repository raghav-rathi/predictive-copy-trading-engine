"""OBV cross signals.

    long_entry  -- OBV crosses above EMA(OBV, 20)
    short_entry -- OBV crosses below EMA(OBV, 20)
    long_exit   -- OBV crosses below EMA(OBV, 20)
    short_exit  -- OBV crosses above EMA(OBV, 20)
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["obv"], df["obv_ema"]).fillna(False)
    down = B.crossed_below(df["obv"], df["obv_ema"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
