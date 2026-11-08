"""Bollinger + RSI(2) indicators.

Bollinger Bands (20, 2): SMA20 +/- 2 x the 20-bar sample standard
deviation of close. RSI(2): Wilder RSI with period 2. Both are causal
(rolling/EWMA over data through bar i), so no lookahead.
"""

import pandas as pd

from strategies.base import bollinger, rsi

BB_PERIOD = 20
BB_K = 2.0
RSI_PERIOD = 2

INDICATOR_COLS = [
    "bb_mid",
    "bb_upper",
    "bb_lower",
    "rsi2",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bands = bollinger(df["c"], BB_PERIOD, BB_K)
    df["bb_mid"] = bands["bb_mid"]
    df["bb_upper"] = bands["bb_upper"]
    df["bb_lower"] = bands["bb_lower"]
    df["rsi2"] = rsi(df["c"], RSI_PERIOD)
    return df
