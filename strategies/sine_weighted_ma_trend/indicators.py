"""Sine-Weighted Moving Average (SWMA) trend crossover.

Weights w_i = sin(pi * (i+1) / (n+1)) over the last n closes
(i=0 oldest, i=n-1 most recent), SWMA = sum(w_i * close_i) / sum(w_i).
The half-sine kernel peaks mid-window, so the average is symmetric,
center-weighted and very smooth -- lag is roughly half the window,
like an SMA of the same length, with better noise suppression.

    swma_fast -- SWMA(close, 20)
    swma_slow -- SWMA(close, 40)
    atr       -- Wilder ATR(14) for the risk layer

No lookahead: each SWMA on bar j uses closes through bar j only;
the first fully-formed value arrives after n bars.
"""

import numpy as np
import pandas as pd

from strategies import base as B

FAST_N = 20  # shipped default
SLOW_N = 40  # shipped default


def swma_weights(n: int) -> np.ndarray:
    """Half-sine weights, oldest -> newest; symmetric, sum > 0."""
    i = np.arange(n, dtype=float)
    return np.sin(np.pi * (i + 1.0) / (n + 1.0))


def swma(c: pd.Series, n: int) -> pd.Series:
    """Sine-weighted moving average of length n."""
    w = swma_weights(n)
    wsum = w.sum()
    return c.rolling(n, min_periods=n).apply(
        lambda x: float(np.dot(w, x)) / wsum, raw=True
    )


def add_indicators(df: pd.DataFrame, fast_n: int = FAST_N,
                   slow_n: int = SLOW_N) -> pd.DataFrame:
    df = df.copy()
    df["swma_fast"] = swma(df["c"], fast_n)
    df["swma_slow"] = swma(df["c"], slow_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
