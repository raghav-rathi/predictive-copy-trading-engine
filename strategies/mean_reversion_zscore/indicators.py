"""Z-score mean reversion indicators.

z = (close - SMA(20)) / std(20) of close. SMA(50) slope is the regime
guard: longs only when the 50-bar SMA is flat-to-up, shorts only when
it is flat-to-down.
"""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["sma20", "zscore", "sma50", "sma50_slope_up", "sma50_slope_down", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["sma20"] = B.sma(df["c"], 20)
    std20 = df["c"].rolling(20, min_periods=20).std()
    df["zscore"] = (df["c"] - df["sma20"]) / std20.replace(0, float("nan"))
    df["sma50"] = B.sma(df["c"], 50)
    sma50_lag10 = df["sma50"].shift(10)
    df["sma50_slope_up"] = (df["sma50"] >= sma50_lag10).astype(bool)
    df["sma50_slope_down"] = (df["sma50"] <= sma50_lag10).astype(bool)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
