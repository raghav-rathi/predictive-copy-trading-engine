"""Wyckoff Sign of Strength indicators.

Wyckoff sign of strength / weakness: a close above the prior 40-bar high on volume over 1.5x its 20-bar average is a sign of strength (long); a close below the prior 40-bar low on the same volume condition is a sign of weakness (short). Exits on close back inside the range.
"""

import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["range_high"] = df["h"].shift(1).rolling(40, min_periods=40).max()
    df["range_low"] = df["l"].shift(1).rolling(40, min_periods=40).min()
    df["avg_vol"] = df["v"].shift(1).rolling(20, min_periods=20).mean()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
