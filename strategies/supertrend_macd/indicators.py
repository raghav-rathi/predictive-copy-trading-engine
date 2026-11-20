"""Supertrend + MACD agreement indicators.

Supertrend(10, 3.0 ATR) from strategies.base (Wilder ATR(10), upper/lower
bands, trend flips when the close crosses the active band; seeded at the
first bar with a valid ATR, using data through that bar only) and
MACD(12, 26, 9) histogram.

Columns:
    supertrend / supertrend_dir -- Supertrend line and direction
        (+1 bullish / -1 bearish, NaN before the ATR warms up)
    macd / macd_signal / macd_hist -- MACD line, signal, histogram
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import pandas as pd

from strategies import base as B

ST_PERIOD = 10
ST_MULT = 3.0
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

INDICATOR_COLS = ["supertrend", "supertrend_dir", "macd", "macd_signal",
                  "macd_hist", "atr"]


def add_indicators(df: pd.DataFrame, st_n: int = ST_PERIOD,
                   st_k: float = ST_MULT, macd_fast: int = MACD_FAST,
                   macd_slow: int = MACD_SLOW,
                   macd_signal: int = MACD_SIGNAL) -> pd.DataFrame:
    df = df.copy()
    st = B.supertrend(df["h"], df["l"], df["c"], st_n, st_k)
    df["supertrend"] = st["supertrend"]
    df["supertrend_dir"] = st["supertrend_dir"]
    m = B.macd(df["c"], macd_fast, macd_slow, macd_signal)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
