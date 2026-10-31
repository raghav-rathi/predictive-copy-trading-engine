"""Hull Moving Average cross indicators (Alan Hull).

WMA(c, n) is the linearly weighted moving average with weights
1..n (most recent bar gets weight n), requiring n bars before it
is defined. HMA(n) = WMA(2*WMA(c, n/2) - WMA(c, n), sqrt(n)).

Columns:
    hma_fast -- HMA(16): WMA(2*WMA(c, 8) - WMA(c, 16), 4)
    hma_slow -- HMA(64): WMA(2*WMA(c, 32) - WMA(c, 64), 8)
    atr      -- Wilder ATR(14) for the risk layer

All windows use only bars up to and including the current bar, so
the indicators are strictly causal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

FAST = 16
SLOW = 64


def wma(s: pd.Series, n: int) -> pd.Series:
    """Linearly weighted moving average, weights 1..n, newest heaviest."""
    weights = np.arange(1, n + 1, dtype=float)
    denom = weights.sum()

    def _wma(window):
        return float(np.dot(window, weights) / denom)

    return s.rolling(n, min_periods=n).apply(_wma, raw=True)


def hma(s: pd.Series, n: int) -> pd.Series:
    """Hull Moving Average of period n (n even; sqrt(n) rounded)."""
    half = n // 2
    raw = 2 * wma(s, half) - wma(s, n)
    sqrt_n = int(round(float(np.sqrt(n))))
    return wma(raw, max(1, sqrt_n))


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hma_fast"] = hma(df["c"], FAST)
    df["hma_slow"] = hma(df["c"], SLOW)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
