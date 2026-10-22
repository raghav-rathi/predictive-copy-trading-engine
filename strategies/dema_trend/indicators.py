"""DEMA -- Double Exponential Moving Average (Patrick Mulloy, TASC Jan 1994).

    EMA1 = EMA(close, n)
    EMA2 = EMA(EMA1, n)
    DEMA = 2*EMA1 - EMA2

Mulloy's construction removes most of the lag of a plain EMA: applying
the EMA a second time isolates the lag component, and subtracting it
(while doubling the first pass) yields a smoothed line that tracks
price about twice as fast as the plain EMA without adding jitter.
Columns:

    dema_fast -- DEMA(close, fast)
    dema_slow -- DEMA(close, slow)
    atr       -- Wilder ATR(14) for the risk layer

No lookahead: every EMA on bar j uses data through bar j only;
ewm(min_periods=n) means each DEMA's first fully-formed value arrives
after ~2*(n-1) bars of data.
"""

import numpy as np
import pandas as pd

from strategies import base as B

FAST = 21  # shipped default
SLOW = 55  # shipped default


def dema(s: pd.Series, n: int) -> pd.Series:
    """Double exponential moving average of the series."""
    ema1 = B.ema(s, n)
    ema2 = B.ema(ema1, n)
    return 2.0 * ema1 - ema2


def add_indicators(df: pd.DataFrame, fast: int = FAST,
                   slow: int = SLOW) -> pd.DataFrame:
    df = df.copy()
    df["dema_fast"] = dema(df["c"], fast)
    df["dema_slow"] = dema(df["c"], slow)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
