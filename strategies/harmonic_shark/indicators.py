"""Harmonic Shark indicators: 2-bar swing pivots + ATR."""

import numpy as np
import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["atr"]


def _pivot_columns(df: pd.DataFrame) -> pd.DataFrame:
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    n = len(df)
    ph = np.full(n, np.nan)
    pl = np.full(n, np.nan)
    for i in range(2, n - 2):
        if h[i] == max(h[i - 2:i + 3]) and (h[i] > h[i - 1] or h[i] > h[i + 1]):
            ph[i] = h[i]
        if l[i] == min(l[i - 2:i + 3]) and (l[i] < l[i - 1] or l[i] < l[i + 1]):
            pl[i] = l[i]
    df["pivot_high"] = ph
    df["pivot_low"] = pl
    return df


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = _pivot_columns(df)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
