"""Dr. Alexander Elder's Elder Ray indicators (1989).

The 13-bar EMA of closes is the market's consensus of value. Bull Power
and Bear Power measure how far each side can push price away from it:

    Bull Power = High - EMA(13)
    Bear Power = Low  - EMA(13)

Elder's classic long setup: the EMA is rising (bulls in control) but
Bear Power is negative and turning up -- sellers are exhausted while
the trend is intact. The short setup mirrors it. All causal: only data
through bar i's close.
"""

import pandas as pd

from strategies import base as B

EMA_N = 13  # Elder's consensus EMA


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ema = B.ema(df["c"], EMA_N)
    df["elder_ema"] = ema
    df["bull_power"] = df["h"] - ema
    df["bear_power"] = df["l"] - ema
    return df
