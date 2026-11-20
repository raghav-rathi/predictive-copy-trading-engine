"""Adaptive MACD signals.

Long entry:  MACD line crosses above its signal line.
Short entry: MACD line crosses below its signal line.
Long exit:   opposite cross (MACD below signal).
Short exit:  opposite cross (MACD above signal).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = crossed_above(df["macd"], df["macd_signal"]).fillna(False).astype(bool)
    df["short_entry"] = crossed_below(df["macd"], df["macd_signal"]).fillna(False).astype(bool)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
