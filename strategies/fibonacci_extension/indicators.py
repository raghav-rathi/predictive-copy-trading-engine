"""Fibonacci retracement zone of the trailing 50-bar range."""

import numpy as np
import pandas as pd

from strategies import base as B

N = 50


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["sma50"] = B.sma(df["c"], N)
    df["fib_high"] = df["h"].rolling(N, min_periods=N).max()
    df["fib_low"] = df["l"].rolling(N, min_periods=N).min()
    df["fib_retr"] = (df["fib_high"] - df["c"]) / (df["fib_high"] - df["fib_low"])
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
