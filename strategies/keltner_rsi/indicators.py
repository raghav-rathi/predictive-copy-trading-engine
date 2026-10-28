"""Keltner channel + RSI indicators (Chester Keltner / Linda Raschke
/ J. Welles Wilder).

Columns:
    kc_mid   -- EMA(20) of close
    kc_upper -- kc_mid + 1.5 * ATR(10)
    kc_lower -- kc_mid - 1.5 * ATR(10)
    rsi      -- Wilder RSI(14)
    atr      -- Wilder ATR(14) for the risk layer

The channel uses the modern Raschke form (EMA midline, ATR width)
rather than Keltner's original SMA/high-low-range form. All causal.
"""

import pandas as pd

from strategies import base as B

EMA_N = 20
ATR_N = 10
MULT = 1.5
RSI_N = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    kc = B.keltner(df["h"], df["l"], df["c"], EMA_N, ATR_N, MULT)
    df["kc_mid"] = kc["kc_mid"]
    df["kc_upper"] = kc["kc_upper"]
    df["kc_lower"] = kc["kc_lower"]
    df["rsi"] = B.rsi(df["c"], RSI_N)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
