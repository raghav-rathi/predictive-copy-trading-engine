"""Supertrend trend-following indicators.

Supertrend (Olivier Seban, public formula): ATR-based trailing band;
direction flips define trend state. ADX(14) > 20 confirmation filter.
"""

import pandas as pd

from strategies import base as B

ST_N = 10
ST_K = 3.0
ADX_MIN = 20.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    st = B.supertrend(df["h"], df["l"], df["c"], ST_N, ST_K)
    df["st_line"] = st["supertrend"]
    df["st_dir"] = st["supertrend_dir"]
    df["st_dir_prev"] = df["st_dir"].shift(1)
    df["adx"] = B.adx(df["h"], df["l"], df["c"], 14)["adx"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
