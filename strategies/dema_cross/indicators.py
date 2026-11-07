"""DEMA crossover indicators: Patrick Mulloy's Double Exponential
Moving Average (Technical Analysis of Stocks & Commodities, 1994).

DEMA(n) = 2*EMA(n) - EMA(EMA(n)). The double smoothing removes much
of the lag of a plain EMA while keeping the smoothing. Fast DEMA(12)
vs slow DEMA(26), computed from closes only, using data through bar
i's close — no lookahead.
"""

import pandas as pd

from strategies import base as B

FAST_N = 12
SLOW_N = 26

INDICATOR_COLS = ["dema_fast", "dema_slow"]


def _dema(c, n: int):
    e1 = B.ema(c, n)
    e2 = B.ema(e1, n)
    return 2 * e1 - e2


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["dema_fast"] = _dema(df["c"], FAST_N)
    df["dema_slow"] = _dema(df["c"], SLOW_N)
    return df
