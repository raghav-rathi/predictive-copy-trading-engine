"""Pring Special K indicators.

Martin Pring Special K: weighted sum of 10/15/20/30-bar ROCs (weights 1/2/3/4), smoothed with a 10-bar MA, traded against its own 10-bar signal line. Long on K cross above signal, short on cross below; exits on the opposite cross.
"""

import pandas as pd

from strategies import base as B


def _roc(c, n):
    return (c / c.shift(n) - 1.0) * 100.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    raw = 1 * _roc(c, 10) + 2 * _roc(c, 15) + 3 * _roc(c, 20) + 4 * _roc(c, 30)
    k = raw.rolling(10, min_periods=10).mean()
    df["special_k"] = k
    df["special_k_signal"] = k.rolling(10, min_periods=10).mean()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
