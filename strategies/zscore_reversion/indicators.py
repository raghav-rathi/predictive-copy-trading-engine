"""Bollinger z-score indicators.

The z-score restates Bollinger Bands in standard-deviation units:
z = (close - SMA(20)) / std(20). The +/-2 levels are exactly the
Bollinger band edges; zero is the middle band.

Columns:
    zscore -- (close - SMA(20)) / std(20); zero when std is zero
    atr    -- Wilder ATR(14) for the risk layer

All windows use only bars up to and including the current bar, so
the indicators are strictly causal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    mid = B.sma(df["c"], PERIOD)
    sd = df["c"].rolling(PERIOD, min_periods=PERIOD).std()
    df["zscore"] = ((df["c"] - mid) / sd.replace(0, np.nan)).fillna(0.0)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
