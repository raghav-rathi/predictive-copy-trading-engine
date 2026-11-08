"""RSI pullback in trend indicators.

Trend: SMA50 vs SMA200. Pullback quality: RSI(14). Only data through
bar i's close is used for bar i's values.
"""

import numpy as np
import pandas as pd

from strategies.base import rsi, sma

INDICATOR_COLS = [
    "sma50",
    "sma200",
    "rsi14",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["sma50"] = sma(df["c"], 50)
    df["sma200"] = sma(df["c"], 200)
    df["rsi14"] = rsi(df["c"], 14)
    return df
