"""Ehlers RSI signals (RSI on SuperSmoother-filtered closes).

Long entry: smoothed RSI crosses above 30 (oversold bounce).
Short entry: smoothed RSI crosses below 70 (overbought fade).
Long exit: smoothed RSI crosses above 70 (overbought — take the win).
Short exit: smoothed RSI crosses below 30 (oversold — cover).

All inputs are computed from data through bar i's close, so signals
on bar i use no future data. The harness executes at bar i+1's open.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

OVERSOLD = 30.0
OVERBOUGHT = 70.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = crossed_above(df["rsi_ss"], OVERSOLD).fillna(False).astype(bool)
    df["short_entry"] = crossed_below(df["rsi_ss"], OVERBOUGHT).fillna(False).astype(bool)
    df["long_exit"] = crossed_above(df["rsi_ss"], OVERBOUGHT).fillna(False).astype(bool)
    df["short_exit"] = crossed_below(df["rsi_ss"], OVERSOLD).fillna(False).astype(bool)
    return df
