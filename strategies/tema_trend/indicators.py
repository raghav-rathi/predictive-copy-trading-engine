"""Triple Exponential Moving Average (TEMA) trend indicators.

Patrick Mulloy's TEMA removes the lag of a single EMA by combining three
nested smoothings:

    EMA1 = EMA(close, n)
    EMA2 = EMA(EMA1, n)
    EMA3 = EMA(EMA2, n)
    TEMA(n) = 3*EMA1 - 3*EMA2 + EMA3

Computed for n=20 (fast) and n=50 (slow), plus SMA200 as the long-term
regime filter. No lookahead: every value on bar i uses bars through i only.
"""

import pandas as pd

from strategies import base as B

TEMA_FAST = 20
TEMA_SLOW = 50
SMA_REGIME = 200


def tema(s: pd.Series, n: int) -> pd.Series:
    e1 = B.ema(s, n)
    e2 = B.ema(e1, n)
    e3 = B.ema(e2, n)
    return 3 * e1 - 3 * e2 + e3


def add_indicators(
    df: pd.DataFrame,
    fast: int = TEMA_FAST,
    slow: int = TEMA_SLOW,
    regime: int = SMA_REGIME,
) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    df["tema_fast"] = tema(c, fast)
    df["tema_slow"] = tema(c, slow)
    df["sma_regime"] = B.sma(c, regime)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
