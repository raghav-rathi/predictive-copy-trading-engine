"""Gap and Go indicators: gap size, relative volume, gap-bar levels."""

import pandas as pd

from strategies import base as B

GAP_MIN = 0.015
VOL_MULT = 2.0
INDICATOR_COLS = ["gap_pct", "rel_vol", "gap_high", "gap_low", "gap_mid"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_c = df["c"].shift(1)
    df["gap_pct"] = (df["o"] - prev_c) / prev_c
    avg_vol = df["v"].rolling(50, min_periods=20).mean()
    df["rel_vol"] = df["v"] / avg_vol.replace(0, float("nan"))
    qual_up = (df["gap_pct"] >= GAP_MIN) & (df["rel_vol"] >= VOL_MULT)
    qual_dn = (df["gap_pct"] <= -GAP_MIN) & (df["rel_vol"] >= VOL_MULT)
    df["gap_high"] = df["h"].where(qual_up).ffill(limit=3)
    df["gap_low"] = df["l"].where(qual_dn).ffill(limit=3)
    df["gap_mid"] = ((df["h"] + df["l"]) / 2).where(qual_up | qual_dn).ffill(limit=3)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
