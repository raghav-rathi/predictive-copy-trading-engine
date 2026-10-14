"""E.S. Coppock's Coppock Curve indicators (Barron's, October 1962).

Coppock = WMA(10) of (ROC(14) + ROC(11)), ROC in percent.
Coppock built it for monthly S&P data to flag long-term buying
opportunities; here it runs on 1h crypto candles as a slow momentum
regime gauge. Signal convention used by the engine: long when the curve
crosses above zero from below, short on the mirror cross below zero
(Coppock himself used only the trough-turn below zero for longs; the
zero-cross is the objective, tradable version). All causal: only data
through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ROC_FAST = 11
ROC_SLOW = 14
WMA_N = 10


def _wma(s: pd.Series, n: int) -> pd.Series:
    w = np.arange(1, n + 1, dtype=float)  # oldest=1 ... newest=n
    return s.rolling(n, min_periods=n).apply(
        lambda x: float((x * w).sum() / w.sum()), raw=True
    )


def _roc(c: pd.Series, n: int) -> pd.Series:
    prev = c.shift(n).replace(0, float("nan"))
    return 100.0 * (c - c.shift(n)) / prev


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    momentum = _roc(c, ROC_SLOW) + _roc(c, ROC_FAST)
    df["coppock"] = _wma(momentum, WMA_N)
    return df
