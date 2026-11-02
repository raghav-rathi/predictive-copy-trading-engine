"""Aroon Oscillator signals.

    long_entry  -- oscillator crosses above 0 (fresh uptrend)
    short_entry -- oscillator crosses below 0 (fresh downtrend)
    long_exit   -- oscillator crosses below 0
    short_exit  -- oscillator crosses above 0
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["aroon_osc"], 0).fillna(False)
    down = B.crossed_below(df["aroon_osc"], 0).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
