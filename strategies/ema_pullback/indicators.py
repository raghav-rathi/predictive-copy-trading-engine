"""EMA Pullback indicators: EMA(20), EMA(50), ATR(14)."""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["ema20", "ema50", "atr14"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema20"] = B.ema(df["c"], 20)
    df["ema50"] = B.ema(df["c"], 50)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
