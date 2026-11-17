"""Triple RSI indicators.

RSI(7), RSI(14) and RSI(21), all Wilder-smoothed via the shared
base.rsi helper.

Columns:

    rsi7, rsi14, rsi21  -- Wilder RSI at the three lookbacks
    atr                 -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import pandas as pd

from strategies import base as B

RSI_FAST = 7
RSI_MID = 14
RSI_SLOW = 21

INDICATOR_COLS = ["rsi7", "rsi14", "rsi21", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi7"] = B.rsi(df["c"], RSI_FAST)
    df["rsi14"] = B.rsi(df["c"], RSI_MID)
    df["rsi21"] = B.rsi(df["c"], RSI_SLOW)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
