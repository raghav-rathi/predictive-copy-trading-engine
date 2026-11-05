"""Turtle Trading indicators: Donchian channels (20 / 55 / 10) + N = ATR(20)."""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = [
    "donchian_high_20",
    "donchian_low_20",
    "donchian_high_55",
    "donchian_low_55",
    "donchian_high_10",
    "donchian_low_10",
    "atr20",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for n in (20, 55, 10):
        d = B.donchian(df["h"], df["l"], n)
        df[f"donchian_high_{n}"] = d[f"donchian_high_{n}"]
        df[f"donchian_low_{n}"] = d[f"donchian_low_{n}"]
    # Turtle N: 20-period ATR.
    df["atr20"] = B.atr(df["h"], df["l"], df["c"], 20)
    return df
