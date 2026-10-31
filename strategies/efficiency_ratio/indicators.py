"""Kaufman Efficiency Ratio (10) + EMA(9)/EMA(21).

ER(10) = |C - C[10]| / sum(|C_i - C_{i-1}| over the last 10 bars).
ER = 1 when price moves the same direction every bar of the window,
ER = 0 when price ends where it started (or is flat). A zero
denominator (perfectly flat window) yields ER = 0, not NaN.
All columns are strictly causal.

Columns:
    er      -- Efficiency Ratio, 0-1 (NaN until 10 changes exist)
    ema9    -- EMA(9) on closes
    ema21   -- EMA(21) on closes
    atr     -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

ER_PERIOD = 10
FAST = 9
SLOW = 21
ER_THRESHOLD = 0.3


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    change = (c - c.shift(ER_PERIOD)).abs()
    volatility = c.diff().abs().rolling(ER_PERIOD, min_periods=ER_PERIOD).sum()
    er = change / volatility
    # Flat window: 0/0 -> 0 (no trend efficiency at all).
    er = er.where(volatility > 0, 0.0)
    df["er"] = er
    df["ema9"] = B.ema(c, FAST)
    df["ema21"] = B.ema(c, SLOW)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
