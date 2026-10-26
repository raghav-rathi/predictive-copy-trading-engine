"""VCP proxy on 1h bars: trend + contraction + pivot breakout.

Contraction is measured honestly as ATR falling vs 20 bars ago and a
tight 20-bar range (<2% of price); the original VCP is a multi-week
daily-base pattern, and this 1h version is a proxy, not the original.
"""

import numpy as np
import pandas as pd

from strategies import base as B

N = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["sma50"] = B.sma(df["c"], 50)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    df["vcp_high"] = df["h"].shift(1).rolling(N, min_periods=N).max()
    df["vcp_low"] = df["l"].shift(1).rolling(N, min_periods=N).min()
    df["vol_avg"] = df["v"].shift(1).rolling(N, min_periods=N).mean()
    df["atr_ratio"] = df["atr"] / df["atr"].shift(20)
    df["range_pct"] = (df["vcp_high"] - df["vcp_low"]) / df["c"]
    return df
