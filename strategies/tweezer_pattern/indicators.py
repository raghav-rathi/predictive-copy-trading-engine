"""Tweezer inputs: equal highs/lows within tolerance."""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
