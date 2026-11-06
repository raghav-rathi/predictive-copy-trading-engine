"""Volume-weighted MACD indicators: 20-bar volume-weighted price, MACD
(12/26/9) computed on it, and a 50-bar SMA trend filter on close."""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["vw_price", "vw_macd", "vw_signal", "vw_hist", "sma50"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pv = (df["c"] * df["v"]).rolling(20, min_periods=20).sum()
    vv = df["v"].rolling(20, min_periods=20).sum()
    df["vw_price"] = pv / vv.replace(0, float("nan"))
    df["vw_macd"] = B.ema(df["vw_price"], 12) - B.ema(df["vw_price"], 26)
    df["vw_signal"] = B.ema(df["vw_macd"], 9)
    df["vw_hist"] = df["vw_macd"] - df["vw_signal"]
    df["sma50"] = B.sma(df["c"], 50)
    return df
