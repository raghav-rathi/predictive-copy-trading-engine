"""Donchian channel (20-bar) indicators."""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["donchian_high_20", "donchian_low_20", "donchian_mid_20"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = B.donchian(df["h"], df["l"], 20)
    df["donchian_high_20"] = d["donchian_high_20"]
    df["donchian_low_20"] = d["donchian_low_20"]
    df["donchian_mid_20"] = (df["donchian_high_20"] + df["donchian_low_20"]) / 2
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
