"""Relative Volatility Index indicators.

Donald Dorsey Relative Volatility Index (10/10): volatility-weighted RSI — standard deviation of closes split into up/down buckets. Long on cross above 50, short on cross below 50; exits on the opposite cross.
"""

import numpy as np
import pandas as pd

from strategies import base as B

STD_PERIOD = 10
SUM_PERIOD = 10


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    std = df["c"].rolling(STD_PERIOD, min_periods=STD_PERIOD).std()
    rising = df["c"].diff() > 0
    falling = df["c"].diff() < 0
    up_vol = std.where(rising, 0.0)
    down_vol = std.where(falling, 0.0)
    up_sum = up_vol.rolling(SUM_PERIOD, min_periods=SUM_PERIOD).sum()
    down_sum = down_vol.rolling(SUM_PERIOD, min_periods=SUM_PERIOD).sum()
    total = up_sum + down_sum
    df["rvi"] = (100.0 * up_sum / total.replace(0, float("nan"))).fillna(50.0)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
