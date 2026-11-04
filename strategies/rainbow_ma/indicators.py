"""Rainbow Moving Average indicators: 22 EMAs, 9 to 100 periods."""

import pandas as pd

from strategies import base as B

PERIODS = [9, 12, 15, 18, 21, 24, 27, 30, 35, 40, 45, 50,
           55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
INDICATOR_COLS = ["rb_max", "rb_min", "rb_fast"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    emas = [B.ema(df["c"], p) for p in PERIODS]
    stacked = pd.concat(emas, axis=1)
    df["rb_max"] = stacked.max(axis=1)
    df["rb_min"] = stacked.min(axis=1)
    df["rb_fast"] = emas[0]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
