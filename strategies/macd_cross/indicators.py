"""MACD(12,26,9) indicators (Gerald Appel, 1979).

    MACD line   = EMA(12) of close - EMA(26) of close
    Signal line = EMA(9) of the MACD line
    Histogram   = MACD line - signal line

Appel's published defaults (12, 26, 9) are used verbatim; the
histogram is carried for diagnostics only and plays no role in the
signals.

Columns:

    macd        -- MACD line
    macd_signal -- 9-period EMA of the MACD line
    macd_hist   -- MACD line minus signal line
    atr         -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
On a flat series both EMAs equal the close, so MACD and the signal
line are both exactly 0.
"""

import pandas as pd

from strategies import base as B

FAST = 12
SLOW = 26
SIGNAL = 9

INDICATOR_COLS = ["macd", "macd_signal", "macd_hist", "atr"]


def add_indicators(df: pd.DataFrame, fast: int = FAST,
                   slow: int = SLOW,
                   signal: int = SIGNAL) -> pd.DataFrame:
    df = df.copy()
    m = B.macd(df["c"], fast=fast, slow=slow, signal=signal)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
