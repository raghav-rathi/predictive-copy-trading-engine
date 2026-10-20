"""ALMA (Arnaud Legoux Moving Average) indicators.

The ALMA is a Gaussian-weighted moving average: for window n, the
weight on position i (i = 0 oldest, n-1 newest) is

    w_i = exp(-((i - offset*(n-1))^2) / (2*sigma^2)),  sigma = 6

normalized to sum 1, with the offset pulling the bell toward the
newest bars (offset=0.85, i.e. the peak sits near the right edge) so
the line hugs price with less lag than a symmetric Gaussian.

ALMA(n) on bar j = sum_{i=0..n-1} w_i * close[j-(n-1)+i]: the newest
close in the window gets the largest weight. Weights are computed
once per (n, offset) and applied with a vectorized rolling dot
product (min_periods=n, so no partially-formed values).

Columns:
    alma_fast -- ALMA(9)  of close
    alma_slow -- ALMA(21) of close
    alma_diff -- alma_fast - alma_slow

No lookahead: the value on bar j uses closes through bar j only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

SIGMA = 6.0
OFFSET = 0.85  # shipped default
FAST_N = 9
SLOW_N = 21


def alma_weights(n: int, offset: float = OFFSET, sigma: float = SIGMA) -> np.ndarray:
    """Gaussian weights, i=0 oldest .. n-1 newest, normalized to sum 1."""
    m = n - 1
    i = np.arange(n, dtype=float)
    w = np.exp(-((i - offset * m) ** 2) / (2.0 * sigma**2))
    s = w.sum()
    if not np.isfinite(s) or s <= 0:
        w = np.ones(n) / n
    else:
        w = w / s
    return w


def alma(series: pd.Series, n: int, offset: float = OFFSET) -> pd.Series:
    """ALMA(n) of close: weight w_0 on the oldest bar, w_{n-1} on the newest."""
    w = alma_weights(n, offset)
    x = series.to_numpy(dtype=float)

    def dot(win):
        return float(np.dot(w, win))

    return series.rolling(n, min_periods=n).apply(dot, raw=True)


def add_indicators(df: pd.DataFrame, offset: float = OFFSET) -> pd.DataFrame:
    df = df.copy()
    df["alma_fast"] = alma(df["c"], FAST_N, offset)
    df["alma_slow"] = alma(df["c"], SLOW_N, offset)
    df["alma_diff"] = df["alma_fast"] - df["alma_slow"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
