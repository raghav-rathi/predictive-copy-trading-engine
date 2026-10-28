"""RSI + MACD confluence indicators (Wilder / Appel).

Columns:
    rsi       -- Wilder RSI(14)
    macd      -- EMA(12) - EMA(26) of close
    macd_signal -- EMA(9) of macd
    macd_hist -- macd - macd_signal
    atr       -- Wilder ATR(14) for the risk layer

All causal: EMAs and Wilder RSI read only data through the current
bar's close.
"""

import pandas as pd

from strategies import base as B

RSI_N = 14
FAST = 12
SLOW = 26
SIGNAL = 9


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = B.rsi(df["c"], RSI_N)
    m = B.macd(df["c"], FAST, SLOW, SIGNAL)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
