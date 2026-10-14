"""Least Squares Moving Average slope indicators.

LSMA(N) is the endpoint of the least-squares regression line fitted over
the last N closes: for x = 0..N-1 (oldest to newest within the window),

    b = (N*sum(x*y) - sum(x)*sum(y)) / (N*sum(x^2) - sum(x)^2)
    a = (sum(y) - b*sum(x)) / N
    LSMA = a + b*(N-1)

Unlike a lagging SMA, the regression endpoint responds to the most
recent data and naturally leads a simple average. Classic length 21.
The slope is the 5-bar change in the LSMA itself. No lookahead: every
bar uses only data through that bar's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

LSMA_LEN = 21
SLOPE_BARS = 5


def _lsma_end(arr: np.ndarray) -> float:
    n = len(arr)
    x = np.arange(n, dtype=float)
    sx = x.sum()
    sx2 = (x * x).sum()
    sy = arr.sum()
    sxy = (arr * x).sum()
    denom = n * sx2 - sx * sx
    b = (n * sxy - sx * sy) / denom
    a = (sy - b * sx) / n
    return a + b * (n - 1)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["lsma"] = (
        df["c"].rolling(LSMA_LEN, min_periods=LSMA_LEN).apply(_lsma_end, raw=True)
    )
    df["lsma_slope"] = df["lsma"] - df["lsma"].shift(SLOPE_BARS)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
