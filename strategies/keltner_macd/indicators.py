"""Keltner(20, 10, 1.5) + MACD(12,26,9) indicators."""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["kc_mid", "kc_upper", "kc_lower", "macd", "macd_signal"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    kc = B.keltner(df["h"], df["l"], df["c"])
    df["kc_mid"] = kc["kc_mid"]
    df["kc_upper"] = kc["kc_upper"]
    df["kc_lower"] = kc["kc_lower"]
    m = B.macd(df["c"])
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
