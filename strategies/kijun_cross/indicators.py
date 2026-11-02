"""Kijun-sen cross indicators (Ichimoku's baseline line).

Kijun-sen = (highest high + lowest low over 26 bars) / 2: the
midpoint of the last 26 bars' range, and Ichimoku's baseline
trend line. Price above it is bullish territory, below it
bearish — this system trades the cross alone, deliberately
without the cloud, Tenkan, or Chikou filters of the full system.

Columns:
    kijun, atr
"""

import pandas as pd

from strategies import base as B

PERIOD = 26


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["kijun"] = (df["h"].rolling(PERIOD).max() + df["l"].rolling(PERIOD).min()) / 2
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
