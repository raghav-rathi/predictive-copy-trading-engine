"""Bollinger + RSI(2) mean-reversion signals.

Long: bar i-1 closed below the lower band with RSI(2) < 10, and bar i
closes back inside the band (close[i] > lower[i]) -> enter on bar i.
Short: mirror — bar i-1 closed above the upper band with RSI(2) > 90,
and bar i closes back inside (close[i] < upper[i]). Exit a long on a
close at/above the middle band or RSI(2) > 90; exit a short on a close
at/below the middle band or RSI(2) < 10. All inputs use data through
bar i's close, so signals on bar i use no future data.
"""

import numpy as np
import pandas as pd

RSI_OVERSOLD = 10
RSI_OVERBOUGHT = 90


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    mid = df["bb_mid"]
    upper = df["bb_upper"]
    lower = df["bb_lower"]
    rsi2 = df["rsi2"]
    prev_long_setup = (c.shift(1) < lower.shift(1)) & (rsi2.shift(1) < RSI_OVERSOLD)
    prev_short_setup = (c.shift(1) > upper.shift(1)) & (rsi2.shift(1) > RSI_OVERBOUGHT)
    df["long_entry"] = (prev_long_setup & (c > lower)).fillna(False).astype(bool)
    df["short_entry"] = (prev_short_setup & (c < upper)).fillna(False).astype(bool)
    df["long_exit"] = ((c >= mid) | (rsi2 > RSI_OVERBOUGHT)).fillna(False).astype(bool)
    df["short_exit"] = ((c <= mid) | (rsi2 < RSI_OVERSOLD)).fillna(False).astype(bool)
    return df
