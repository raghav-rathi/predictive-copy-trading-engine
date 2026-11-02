"""Ichimoku Kumo breakout indicators.

Senkou Span A = (Tenkan + Kijun) / 2, Senkou Span B = the 52-bar
midpoint, both plotted 26 bars forward — so on bar i the cloud
values were fixed from data at least 26 bars old and are strictly
causal. The cloud top/bottom are the traded levels.

Columns:
    tenkan, kijun, senkou_a, senkou_b, cloud_top, cloud_bottom, atr
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ich = B.ichimoku(df["h"], df["l"], df["c"], 9, 26, 52)
    for col in ich.columns:
        df[col] = ich[col]
    both = df["senkou_a"].notna() & df["senkou_b"].notna()
    df["cloud_top"] = np.where(both, df[["senkou_a", "senkou_b"]].max(axis=1), np.nan)
    df["cloud_bottom"] = np.where(both, df[["senkou_a", "senkou_b"]].min(axis=1), np.nan)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
