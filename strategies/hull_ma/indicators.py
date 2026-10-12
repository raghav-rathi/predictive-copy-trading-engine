"""Alan Hull's Hull Moving Average (HMA) indicators.

HMA(n) = WMA(2*WMA(close, n/2) - WMA(close, n), sqrt(n)), where WMA is the
linearly-weighted moving average. Hull's construction cuts lag versus a
SMA of similar smoothness: the 2*WMA(n/2) - WMA(n) term extrapolates the
recent slope, and the final sqrt(n) WMA re-smooths it. Classic n=16
(half=8, sqrt=4). All causal: only data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

N = 16  # Hull's classic period


def _wma(s: pd.Series, n: int) -> pd.Series:
    w = np.arange(1, n + 1, dtype=float)
    wsum = w.sum()

    def _apply(x):
        return float(np.dot(x, w)) / wsum

    return s.rolling(n, min_periods=n).apply(_apply, raw=True)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    half = max(1, N // 2)
    sqrtn = max(1, int(round(N**0.5)))
    raw = 2.0 * _wma(c, half) - _wma(c, N)
    hma = _wma(raw, sqrtn)
    df["hma"] = hma
    df["hma_slope"] = hma - hma.shift(1)
    return df
