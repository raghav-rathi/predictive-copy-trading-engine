"""Hull Moving Average crossover indicators (Alan Hull, 2005).

HMA(n) = WMA(2 * WMA(n/2) - WMA(n), sqrt(n))
  fast HMA(16): WMA(2*WMA(8) - WMA(16), 4)
  slow HMA(32): WMA(2*WMA(16) - WMA(32), 6)   [sqrt(32) = 5.66, rounded to 6]

NOTE: Alan Hull himself warned against HMA crossovers — they reintroduce
the lag/whipsaw the HMA was designed to remove. This is a test of the
popular retail crossover variant, not Hull's recommended slope method.
"""

import math

import numpy as np
import pandas as pd

from strategies import base as B

FAST_N = 16
SLOW_N = 32

INDICATOR_COLS = ["hma_fast", "hma_slow"]


def wma(s: pd.Series, n: int) -> pd.Series:
    """Linearly weighted moving average (weights 1..n, most recent heaviest)."""
    weights = np.arange(1, n + 1, dtype=float)
    wsum = weights.sum()
    return s.rolling(n, min_periods=n).apply(
        lambda x: float(np.dot(x, weights)) / wsum, raw=True
    )


def hma(s: pd.Series, n: int) -> pd.Series:
    half = max(1, n // 2)
    sqrt_n = max(1, int(round(math.sqrt(n))))
    raw = 2 * wma(s, half) - wma(s, n)
    return wma(raw, sqrt_n)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hma_fast"] = hma(df["c"], FAST_N)
    df["hma_slow"] = hma(df["c"], SLOW_N)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
