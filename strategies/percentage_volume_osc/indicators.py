"""Percentage Volume Oscillator indicators: PVO(12, 26, 9) on volume."""

import pandas as pd

from strategies import base as B

FAST, SLOW, SIGNAL = 12, 26, 9
INDICATOR_COLS = ["pvo", "pvo_signal", "sma50"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast = B.ema(df["v"], FAST)
    slow = B.ema(df["v"], SLOW)
    df["pvo"] = 100.0 * (fast - slow) / slow.replace(0, float("nan"))
    df["pvo_signal"] = B.ema(df["pvo"], SIGNAL)
    df["sma50"] = B.sma(df["c"], 50)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
