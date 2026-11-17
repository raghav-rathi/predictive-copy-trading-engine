"""Supertrend + RSI indicators.

Supertrend(10, 3.0): standard ATR-based Supertrend, Wilder
ATR(10), via the shared ``strategies.base.supertrend`` helper
(bands ratchet: the upper band only falls, the lower band only
rises; direction flips when the close crosses the opposing band).
The shipped line is the lower band while direction is +1 (up) and
the upper band while direction is -1 (down).

RSI(14): Wilder RSI via the shared ``strategies.base.rsi`` helper.

Columns:

    supertrend     -- Supertrend line value at this bar
    supertrend_dir -- +1 (up) / -1 (down); NaN before the first
                      valid ATR bar
    rsi            -- Wilder RSI(14)
    atr            -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import pandas as pd

from strategies import base as B

SUPERTREND_N = 10
SUPERTREND_MULT = 3.0
RSI_N = 14

INDICATOR_COLS = ["supertrend", "supertrend_dir", "rsi", "atr"]


def add_indicators(df: pd.DataFrame, n: int = SUPERTREND_N,
                   mult: float = SUPERTREND_MULT,
                   rsi_n: int = RSI_N) -> pd.DataFrame:
    df = df.copy()
    st = B.supertrend(df["h"], df["l"], df["c"], n, mult)
    df["supertrend"] = st["supertrend"]
    df["supertrend_dir"] = st["supertrend_dir"]
    df["rsi"] = B.rsi(df["c"], rsi_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
