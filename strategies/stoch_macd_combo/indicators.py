"""Stochastic(14,3) + MACD(12,26,9) indicators."""

import pandas as pd

from strategies import base as B

K_PERIOD, D_PERIOD = 14, 3
INDICATOR_COLS = ["stoch_k", "stoch_d", "macd", "macd_signal"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ll = df["l"].rolling(K_PERIOD, min_periods=K_PERIOD).min()
    hh = df["h"].rolling(K_PERIOD, min_periods=K_PERIOD).max()
    rng = (hh - ll).replace(0, float("nan"))
    df["stoch_k"] = 100.0 * (df["c"] - ll) / rng
    df["stoch_d"] = df["stoch_k"].rolling(D_PERIOD, min_periods=D_PERIOD).mean()
    m = B.macd(df["c"])
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
