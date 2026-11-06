"""Stochastic Divergence indicators: slow %K(14,3), %D(3), SMA(50).

Slow %K is the 3-bar SMA of fast %K = 100 * (close - lowest low 14) /
(highest high 14 - lowest low 14); %D is the 3-bar SMA of slow %K.
A zero 14-bar range yields %K = 50 (neutral) instead of a division error.
"""

import numpy as np
import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["stoch_k", "stoch_d", "sma50"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ll = df["l"].rolling(14, min_periods=14).min()
    hh = df["h"].rolling(14, min_periods=14).max()
    rng = hh - ll
    fast_k = 100 * (df["c"] - ll) / rng.replace(0, np.nan)
    fast_k = fast_k.fillna(50.0)
    df["stoch_k"] = fast_k.rolling(3, min_periods=3).mean()
    df["stoch_d"] = df["stoch_k"].rolling(3, min_periods=3).mean()
    df["sma50"] = B.sma(df["c"], 50)
    return df
