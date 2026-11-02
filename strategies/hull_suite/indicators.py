"""Hull Suite indicators (InSilico's Hull Suite, Alan Hull's HMA).

HMA(16) = WMA(2 * WMA(close, 8) - WMA(close, 16), 4): the fast
weighted average is doubled and the slow one subtracted, then the
result is smoothed over sqrt(16) = 4 bars. The Suite's signal is
the line's own turn: rising HMA is bullish, falling HMA bearish.
ATR bands are plotted for context only.

Columns:
    hma, hma_upper, hma_lower, atr
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 16


def _wma(s, n: int):
    w = np.arange(1, n + 1, dtype=float)
    return s.rolling(n).apply(lambda x: float(np.dot(x, w) / w.sum()), raw=True)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    half = 2 * _wma(df["c"], PERIOD // 2) - _wma(df["c"], PERIOD)
    df["hma"] = _wma(half, int(round(PERIOD ** 0.5)))
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    df["hma_upper"] = df["hma"] + 1.5 * df["atr"]
    df["hma_lower"] = df["hma"] - 1.5 * df["atr"]
    return df
