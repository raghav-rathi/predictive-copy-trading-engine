"""StatOasis Rule 4 indicators: multi-indicator momentum.

Pipeline, computed bar by bar using only data through bar i:

1. RSI(14) — Wilder, on the close.
2. Stochastic %K(14, smooth 3): raw %K = 100 * (c - lowest
   low(14)) / (highest high(14) - lowest low(14)), smoothed
   with a 3-bar SMA.
3. Williams %R(14) = -100 * (highest high(14) - c) /
   (highest high(14) - lowest low(14)).
4. 120h return = c / c[-120] - 1. The source is daily SPY with
   a 5-day return and a 10-bar hold; adapted to 1h bars as a
   120-hour (5-day) return and a 10-hour hold, per the brief.

No lookahead: every column is a rolling window / shift over
bars <= i. ATR(14) is included for the risk layer.
"""

import numpy as np
import pandas as pd

from strategies import base as B

RSI_N = 14
STOCH_N = 14
STOCH_SMOOTH = 3
WILLR_N = 14
RET_N = 120


def stochastic_k(h, l, c, n: int = STOCH_N, smooth: int = STOCH_SMOOTH):
    """%K(14) smoothed with a 3-bar SMA; NaN until n bars."""
    ll = l.rolling(n, min_periods=n).min()
    hh = h.rolling(n, min_periods=n).max()
    rng = (hh - ll).replace(0, np.nan)
    raw = 100.0 * (c - ll) / rng
    return raw.rolling(smooth, min_periods=smooth).mean()


def williams_r(h, l, c, n: int = WILLR_N):
    """Williams %R(14), range [-100, 0]; NaN until n bars."""
    ll = l.rolling(n, min_periods=n).min()
    hh = h.rolling(n, min_periods=n).max()
    rng = (hh - ll).replace(0, np.nan)
    return -100.0 * (hh - c) / rng


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = B.rsi(df["c"], RSI_N)
    df["stoch_k"] = stochastic_k(df["h"], df["l"], df["c"])
    df["willr"] = williams_r(df["h"], df["l"], df["c"])
    df["ret_120h"] = df["c"] / df["c"].shift(RET_N) - 1.0
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
