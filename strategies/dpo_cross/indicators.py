"""Detrended Price Oscillator indicators.

DPO removes the long-term trend so short cycles stand out: it compares
the current close with the 20-bar SMA value from 11 bars ago (the
displacement 20/2 + 1 centers the average in its window). The causal
form used here subtracts the displaced average from the current close,
so no future bar is ever read.

Columns:
    dpo -- close minus SMA(20) displaced back 11 bars
    atr -- Wilder ATR(14) for the risk layer

All windows use only bars up to and including the current bar, so
the indicators are strictly causal.
"""

import pandas as pd

from strategies import base as B

PERIOD = 20
SHIFT = PERIOD // 2 + 1


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["dpo"] = df["c"] - B.sma(df["c"], PERIOD).shift(SHIFT)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
