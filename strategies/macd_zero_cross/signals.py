"""MACD zero-line cross signals.

    long_entry  -- MACD line crosses above 0
    short_entry -- MACD line crosses below 0
    long_exit   -- MACD line crosses back below 0 (opposite cross)
    short_exit  -- MACD line crosses back above 0 (opposite cross)

The zero line is the trend filter itself: above zero the fast EMA
leads the slow EMA (uptrend), below zero the reverse. Entries and
exits are the same cross events, so a position reverses on the
opposite cross. Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    macd = df["macd"]
    df["long_entry"] = crossed_above(macd, 0).fillna(False).astype(bool)
    df["short_entry"] = crossed_below(macd, 0).fillna(False).astype(bool)
    df["long_exit"] = crossed_below(macd, 0).fillna(False).astype(bool)
    df["short_exit"] = crossed_above(macd, 0).fillna(False).astype(bool)
    return df
