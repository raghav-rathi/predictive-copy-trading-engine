"""Supertrend direction + ADX strength gate."""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    st = B.supertrend(df["h"], df["l"], df["c"], 10, 3.0)
    df["st_dir"] = st["supertrend_dir"]
    adx = B.adx(df["h"], df["l"], df["c"], 14)
    df["adx"] = adx["adx"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
