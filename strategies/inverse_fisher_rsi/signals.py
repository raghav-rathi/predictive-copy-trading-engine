"""Inverse Fisher RSI threshold signals.

    long_entry  -- IFish crosses above -0.5 (leaving the bearish pole)
    short_entry -- IFish crosses below +0.5 (leaving the bullish pole)
    long_exit   -- IFish crosses below +0.5 (bullish pole lost)
    short_exit  -- IFish crosses above -0.5 (bearish pole lost)

Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    le = B.crossed_above(df["ifish"], -0.5).fillna(False)
    se = B.crossed_below(df["ifish"], 0.5).fillna(False)
    lx = B.crossed_below(df["ifish"], 0.5).fillna(False)
    sx = B.crossed_above(df["ifish"], -0.5).fillna(False)
    df["long_entry"] = le.astype(bool)
    df["short_entry"] = se.astype(bool)
    df["long_exit"] = lx.astype(bool)
    df["short_exit"] = sx.astype(bool)
    return df
