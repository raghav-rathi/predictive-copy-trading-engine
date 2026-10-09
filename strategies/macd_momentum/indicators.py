"""MACD momentum indicators (Gerald Appel, public).

Trend filter: close vs EMA(200). Momentum trigger: MACD histogram
crossing zero. Enter in the trend direction when momentum turns.
"""

import pandas as pd

from strategies import base as B

FAST = 12
SLOW = 26
SIGNAL = 9
TREND_N = 200


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    m = B.macd(df["c"], FAST, SLOW, SIGNAL)
    df["macd_hist"] = m["macd_hist"]
    df["macd_hist_prev"] = df["macd_hist"].shift(1)
    df["ema200"] = B.ema(df["c"], TREND_N)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
