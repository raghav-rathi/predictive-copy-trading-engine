"""Pi Cycle Top indicators (Philip Swift, 2019).

The Pi Cycle Top indicator compares two simple moving averages of
the close:

    sma111  = SMA(close, 111)
    sma350  = SMA(close, 350)
    pi_top  = MULTIPLIER * sma350        (shipped MULTIPLIER = 2.0)

The "top zone" is where sma111 >= 2.0 * sma350. Historically (BTC
daily), the 111-day average crossing above twice the 350-day
average marked cycle tops; the indicator is a regime gauge, not a
timing trigger — on 1h bars the averages move slowly and crossings
are rare (expect a handful of trades per multi-month window at
most).

Columns:
    sma111   -- SMA(close, 111)
    sma350   -- SMA(close, 350)
    pi_top   -- MULTIPLIER * sma350
    pi_ratio -- sma111 / sma350 (1.0 = averages equal; 2.0 = top zone)

No lookahead: rolling windows with min_periods=n use data through
bar j's close only.
"""

import pandas as pd

from strategies import base as B

FAST_N = 111
SLOW_N = 350
MULT = 2.0  # shipped default


def add_indicators(
    df: pd.DataFrame,
    fast_n: int = FAST_N,
    slow_n: int = SLOW_N,
    mult: float = MULT,
) -> pd.DataFrame:
    df = df.copy()
    df["sma111"] = B.sma(df["c"], fast_n)
    df["sma350"] = B.sma(df["c"], slow_n)
    df["pi_top"] = mult * df["sma350"]
    df["pi_ratio"] = df["sma111"] / df["sma350"]
    return df
