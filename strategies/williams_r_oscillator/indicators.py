"""Williams %R(14) + SMA(50) trend filter indicators."""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["williams_r", "sma50"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hh = df["h"].rolling(14, min_periods=14).max()
    ll = df["l"].rolling(14, min_periods=14).min()
    df["williams_r"] = (hh - df["c"]) / (hh - ll).replace(0, float("nan")) * -100.0
    df["sma50"] = B.sma(df["c"], 50)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
