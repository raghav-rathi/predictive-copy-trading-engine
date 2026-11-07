"""MACD zero-line cross indicators.

MACD(12, 26, 9): MACD line = EMA(12) - EMA(26) of close, signal line =
EMA(9) of the MACD line, histogram = line - signal. A zero-line cross
is a pure momentum regime flip: the fast EMA overtaking the slow EMA
(long) or falling below it (short). All values use only data through
the current bar's close — no lookahead.
"""

import pandas as pd

from strategies import base as B

FAST = 12
SLOW = 26
SIGNAL = 9

INDICATOR_COLS = [
    "macd_line",
    "macd_signal",
    "macd_hist",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    macd = B.macd(df["c"], FAST, SLOW, SIGNAL)
    df["macd_line"] = macd["macd"]
    df["macd_signal"] = macd["macd_signal"]
    df["macd_hist"] = macd["macd_hist"]
    return df
