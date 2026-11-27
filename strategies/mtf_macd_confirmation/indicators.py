"""Multi-timeframe MACD confirmation indicators.

1h MACD(12, 26, 9) from strategies.base.macd; 4h MACD(12, 26, 9)
from strategies.timeframes.macd_4h_aligned, which maps only
COMPLETED 4h bars onto the 1h grid (a 1h bar sees the 4h bar
that closed at or before its open) -- no lookahead. The 4h
MACD histogram is NaN until ~34 completed 4h bars (~136 1h
bars): the slow EMA needs 26 4h bars and the signal EMA 9
more. ATR(14) is included for the risk layer.

Columns:

    macd, macd_signal, macd_hist       -- 1h MACD(12, 26, 9)
    macd_4h, macd_signal_4h, macd_hist_4h -- 4h MACD, aligned
    atr14                              -- Wilder ATR(14)

No lookahead: both MACDs are causal EMA constructions, and
the 4h mapping is a backward as-of join on the 4h bar's close
time (see strategies/timeframes.py).
"""

import pandas as pd

from strategies import base as B
from strategies import timeframes as TF

FAST = 12
SLOW = 26
SIGNAL = 9


def add_indicators(
    df: pd.DataFrame,
    fast: int = FAST,
    slow: int = SLOW,
    signal: int = SIGNAL,
) -> pd.DataFrame:
    df = df.copy()
    m = B.macd(df["c"], fast, slow, signal)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df = TF.macd_4h_aligned(df, fast, slow, signal)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
