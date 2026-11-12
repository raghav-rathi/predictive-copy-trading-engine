"""Bull Power / Bear Power indicators (Alexander Elder, 1993).

Elder's Elder-Ray index (Trading for a Living, 1993) measures how far
each bar's high and low stretch from the consensus value, an EMA(13)
of the close:

    Bull Power = high - EMA(13)
    Bear Power = low  - EMA(13)

Bull Power above zero means buyers lifted the high above the average
consensus; Bear Power below zero means sellers drove the low below it.
Elder's buy signal is Bear Power negative but rising (sellers losing
strength) while Bull Power stays positive; the sell signal is the
mirror.

Columns:

    ema13      -- EMA(13) of close (consensus value)
    bull_power -- high - EMA(13)
    bear_power -- low  - EMA(13)
    atr        -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import pandas as pd

from strategies import base as B

EMA_N = 13

INDICATOR_COLS = ["ema13", "bull_power", "bear_power", "atr"]


def add_indicators(df: pd.DataFrame, n: int = EMA_N) -> pd.DataFrame:
    df = df.copy()
    ema13 = B.ema(df["c"], n)
    df["ema13"] = ema13
    df["bull_power"] = df["h"] - ema13
    df["bear_power"] = df["l"] - ema13
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
