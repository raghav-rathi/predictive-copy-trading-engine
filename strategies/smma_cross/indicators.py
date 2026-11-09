"""Wilder's Smoothed Moving Average (SMMA) indicators.

SMMA(n) is Wilder's smoothing: the first value is the simple average
of the first n closes, then each new value is
    SMMA[i] = (SMMA[i-1] * (n-1) + close[i]) / n
i.e. an EMA with alpha = 1/n. All computation is causal (bar i uses
only closes through bar i). Wilder introduced it in "New Concepts in
Technical Trading Systems" (1978) as the smoothing behind RSI/ADX.
"""

import numpy as np
import pandas as pd

FAST_PERIOD = 9
SLOW_PERIOD = 21

INDICATOR_COLS = [
    "smma_fast",
    "smma_slow",
]


def smma(s: pd.Series, n: int) -> pd.Series:
    """Wilder's smoothed MA: SMA-seeded, then alpha = 1/n recursion."""
    c = s.to_numpy(dtype=float)
    out = np.full(len(c), np.nan)
    if len(c) >= n:
        out[n - 1] = c[:n].mean()
        for i in range(n, len(c)):
            out[i] = (out[i - 1] * (n - 1) + c[i]) / n
    return pd.Series(out, index=s.index)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["smma_fast"] = smma(df["c"], FAST_PERIOD)
    df["smma_slow"] = smma(df["c"], SLOW_PERIOD)
    return df
