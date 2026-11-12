"""MACD histogram indicators (Gerald Appel, late 1970s).

MACD line   = EMA(12) of close - EMA(26) of close.
Signal line = EMA(9) of the MACD line.
Histogram   = MACD line - signal line.

The histogram was added by Thomas Aspray (1986) as a visualisation of
the MACD/signal gap; a histogram zero cross is exactly a MACD/signal
line cross, shown as bars. All three are Appel's published defaults
(12, 26, 9), computed with the shared strategies.base.macd primitive
(pandas ewm, adjust=False, seeded at the first close).

Columns:

    macd         -- EMA(12) - EMA(26)
    macd_signal  -- EMA(9) of the MACD line
    macd_hist    -- MACD line - signal line
    atr          -- Wilder ATR(14) for the risk layer

No lookahead: every EMA on bar i uses data through bar i's close.
The histogram is NaN until the signal EMA has 9 valid MACD values
(bar ~34); signals treat NaN as no signal.
"""

import pandas as pd

from strategies import base as B

FAST = 12
SLOW = 26
SIGNAL = 9

INDICATOR_COLS = ["macd", "macd_signal", "macd_hist", "atr"]


def add_indicators(df: pd.DataFrame, fast: int = FAST, slow: int = SLOW,
                   signal: int = SIGNAL) -> pd.DataFrame:
    df = df.copy()
    m = B.macd(df["c"], fast=fast, slow=slow, signal=signal)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
