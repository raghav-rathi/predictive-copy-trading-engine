"""MACD + session VWAP indicators.

  macd         -- MACD line: EMA(12) - EMA(26)
  macd_signal  -- signal line: EMA(9) of the MACD line
  macd_hist    -- MACD line minus signal line
  vwap_day     -- session (UTC-day) VWAP, reset at each UTC midnight
                 (shared strategies.base.anchored_vwap; typical price
                 weighted by volume, cumulative within the day)
  atr          -- Wilder ATR(14) for the risk layer

All computation is causal: every value on bar i uses only data through
bar i's close (the VWAP accumulates only bars of the same UTC day up
to and including bar i).
"""

import pandas as pd

from strategies import base as B

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

INDICATOR_COLS = [
    "macd",
    "macd_signal",
    "macd_hist",
    "vwap_day",
    "atr",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    m = B.macd(df["c"], MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["vwap_day"] = B.anchored_vwap(df["h"], df["l"], df["c"],
                                     df["v"], df["t"])
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
