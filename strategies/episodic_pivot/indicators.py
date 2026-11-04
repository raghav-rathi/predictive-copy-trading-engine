"""Episodic Pivot indicators: gap, relative volume, dull-base filter."""

import pandas as pd

from strategies import base as B

GAP_MIN = 0.02
VOL_MULT = 3.0
INDICATOR_COLS = ["gap_pct", "rel_vol", "quiet_base", "base_high", "sma20"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_c = df["c"].shift(1)
    df["gap_pct"] = (df["o"] - prev_c) / prev_c
    avg_vol = df["v"].rolling(50, min_periods=20).mean()
    df["rel_vol"] = df["v"] / avg_vol.replace(0, float("nan"))
    atr = B.atr(df["h"], df["l"], df["c"], 14)
    df["quiet_base"] = atr <= atr.rolling(50, min_periods=20).median()
    df["base_high"] = df["h"].rolling(20, min_periods=5).max().shift(1)
    df["sma20"] = B.sma(df["c"], 20)
    df["atr"] = atr
    return df
