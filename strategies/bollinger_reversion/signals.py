"""Bollinger Bands %b mean-reversion signals.

Long entry:  close below the lower band (tag, %b <= 0).
Short entry: close above the upper band (tag, %b >= 1).
Long exit:   close back at/above the middle band (SMA(20)).
Short exit:  close back at/below the middle band.

No extra filter — the band tag IS the signal. Signal columns are
boolean, no NaN, no lookahead (the harness executes at the next
bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    lower = df["bb_lower"]
    upper = df["bb_upper"]
    mid = df["bb_mid"]
    df["long_entry"] = (c < lower).fillna(False).astype(bool)
    df["short_entry"] = (c > upper).fillna(False).astype(bool)
    df["long_exit"] = (c >= mid).fillna(False).astype(bool)
    df["short_exit"] = (c <= mid).fillna(False).astype(bool)
    return df
