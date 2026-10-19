"""Cumulative Volume Delta + divergence indicators.

Per-bar volume delta via the close-location approximation:
    delta_i = v_i * (2*c_i - h_i - l_i) / (h_i - l_i)   (0 when h == l)
CVD = cumulative sum of delta.

Price pivots: a bar is a pivot low (high) when its close is the unique
minimum (maximum) of the trailing 10-bar window.

Note: this is an approximation of true trade-direction volume delta
(Hyperliquid 1h candles do not publish tick buy/sell volume). See
BACKTEST.md Limitations.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT_N = 10
LOOKBACK = 60


def add_indicators(
    df: pd.DataFrame,
    pivot_n: int = PIVOT_N,
) -> pd.DataFrame:
    df = df.copy()
    c, h, l, v = df["c"], df["h"], df["l"], df["v"]
    rng = h - l
    loc = (2.0 * c - h - l) / rng.replace(0.0, np.nan)
    delta = (v * loc).fillna(0.0)
    df["delta"] = delta
    df["cvd"] = delta.cumsum()
    # argmin returns the FIRST occurrence, so == n-1 means the last bar is
    # the unique min/max of the window
    argmin_pos = c.rolling(pivot_n, min_periods=pivot_n).apply(np.argmin, raw=True)
    argmax_pos = c.rolling(pivot_n, min_periods=pivot_n).apply(np.argmax, raw=True)
    df["pivot_low"] = (argmin_pos == pivot_n - 1).fillna(False)
    df["pivot_high"] = (argmax_pos == pivot_n - 1).fillna(False)
    df["atr"] = B.atr(h, l, c, 14)
    return df
