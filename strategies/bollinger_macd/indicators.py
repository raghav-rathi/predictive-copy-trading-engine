"""Bollinger(20, 2.0) band tag + MACD(12,26,9) cross indicators.

Long: MACD crosses above its signal line AND the low touched or
      pierced the lower Bollinger band within the last 3 bars.
Short: MACD crosses below its signal line AND the high touched
       or pierced the upper band within the last 3 bars.

Bollinger via strategies.base.bollinger, MACD via
strategies.base.macd.

Columns:
    bb_mid     -- Bollinger middle (SMA 20)
    bb_upper   -- Bollinger upper band
    bb_lower   -- Bollinger lower band
    macd       -- MACD line (EMA12 - EMA26)
    macd_signal-- EMA9 of the MACD line
    macd_hist  -- macd - macd_signal
    atr        -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import pandas as pd

from strategies import base as B

BB_PERIOD = 20
BB_K = 2.0
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

INDICATOR_COLS = ["bb_mid", "bb_upper", "bb_lower", "macd",
                  "macd_signal", "macd_hist", "atr"]


def add_indicators(df: pd.DataFrame, bb_n: int = BB_PERIOD,
                   bb_k: float = BB_K, fast: int = MACD_FAST,
                   slow: int = MACD_SLOW,
                   signal: int = MACD_SIGNAL) -> pd.DataFrame:
    df = df.copy()
    bb = B.bollinger(df["c"], bb_n, bb_k)
    df["bb_mid"] = bb["bb_mid"]
    df["bb_upper"] = bb["bb_upper"]
    df["bb_lower"] = bb["bb_lower"]
    m = B.macd(df["c"], fast, slow, signal)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
