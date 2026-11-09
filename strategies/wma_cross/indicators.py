"""Weighted Moving Average (WMA) indicators.

WMA(n) weights the last n closes linearly, newest first:
    WMA[i] = sum_{k=0}^{n-1} (n-k) * close[i-k] / (n*(n+1)/2)
All computation is causal (bar i uses only closes through bar i).
"""

import numpy as np
import pandas as pd

FAST_PERIOD = 9
SLOW_PERIOD = 21

INDICATOR_COLS = [
    "wma_fast",
    "wma_slow",
]


def wma(s: pd.Series, n: int) -> pd.Series:
    """Linearly weighted MA, newest close weighted n, oldest 1."""
    c = s.to_numpy(dtype=float)
    out = np.full(len(c), np.nan)
    if len(c) >= n:
        weights = np.arange(n, 0, -1, dtype=float)  # n, n-1, ..., 1
        conv = np.convolve(c, weights, mode="valid") / weights.sum()
        out[n - 1:] = conv
    return pd.Series(out, index=s.index)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["wma_fast"] = wma(df["c"], FAST_PERIOD)
    df["wma_slow"] = wma(df["c"], SLOW_PERIOD)
    return df
