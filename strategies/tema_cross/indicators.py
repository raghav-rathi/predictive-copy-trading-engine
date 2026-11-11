"""TEMA(9) vs TEMA(21) cross indicators (Patrick Mulloy).

Triple Exponential Moving Average removes the lag of a single EMA by
combining three nested smoothings:

    EMA1 = EMA(close, n)
    EMA2 = EMA(EMA1, n)
    EMA3 = EMA(EMA2, n)
    TEMA(n) = 3*EMA1 - 3*EMA2 + EMA3

Same formula as strategies/tema_trend, but with faster lengths
(9 / 21) and NO regime filter -- the cross itself is the system.

All computation is causal: every value on bar i uses only data through
bar i's close.
"""

import pandas as pd

from strategies import base as B

TEMA_FAST = 9
TEMA_SLOW = 21

INDICATOR_COLS = ["tema_fast", "tema_slow", "atr"]


def tema(s: pd.Series, n: int) -> pd.Series:
    e1 = B.ema(s, n)
    e2 = B.ema(e1, n)
    e3 = B.ema(e2, n)
    return 3 * e1 - 3 * e2 + e3


def add_indicators(
    df: pd.DataFrame,
    fast: int = TEMA_FAST,
    slow: int = TEMA_SLOW,
) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    df["tema_fast"] = tema(c, fast)
    df["tema_slow"] = tema(c, slow)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
