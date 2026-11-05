"""ADX trend system indicators (Wilder, 1978): ADX(14) with +DI / -DI."""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["adx", "plus_di", "minus_di", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = B.adx(df["h"], df["l"], df["c"], 14)
    df["adx"] = d["adx"]
    df["plus_di"] = d["plus_di"]
    df["minus_di"] = d["minus_di"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
