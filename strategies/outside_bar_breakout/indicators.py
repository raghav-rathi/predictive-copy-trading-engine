"""Outside Bar indicators: engulfing-range bars + close position."""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["outside_bull", "outside_bear"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_h = df["h"].shift(1)
    prev_l = df["l"].shift(1)
    outside = (df["h"] > prev_h) & (df["l"] < prev_l)
    pos = (df["c"] - df["l"]) / (df["h"] - df["l"]).replace(0, float("nan"))
    df["outside_bull"] = (outside & (pos > 2 / 3)).fillna(False)
    df["outside_bear"] = (outside & (pos < 1 / 3)).fillna(False)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
