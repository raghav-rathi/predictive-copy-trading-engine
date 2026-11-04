"""Elliott Wave Oscillator indicators.

EWO = SMA(5) - SMA(35) of closes (Bill Williams 5/35 oscillator; the
5/34 variant differs only in the slow period). SMA(50) slope is the
trend filter: trade zero crosses only in the filter's direction.
"""

import pandas as pd

from strategies import base as B

FAST = 5
SLOW = 35
FILTER = 50
INDICATOR_COLS = ["ewo", "sma50"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ewo"] = B.sma(df["c"], FAST) - B.sma(df["c"], SLOW)
    df["sma50"] = B.sma(df["c"], FILTER)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
