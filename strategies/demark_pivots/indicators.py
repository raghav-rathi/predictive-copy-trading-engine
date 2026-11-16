"""Tom DeMark conditional pivot points.

DeMark pivots differ from classic pivots by conditioning the pivot
on the prior period's close vs open:

    X = H + 2L + C   if C < O
    X = 2H + L + C   if C > O
    X = H + L + 2C   if C == O
    R1 = X/2 - L
    S1 = X/2 - H

The classic daily pivot is computed from one day's OHLC; here the
"day" is the prior 24 bars of 1h candles (H/L = 24-bar high/low,
O/C = the open/close 24 bars ago), so the levels roll forward every
hour. Only one resistance and one support level exist per period —
that is the whole DeMark family (classic_pivots and woodie_pivots
already cover the multi-level families).

    demark_x   -- conditional pivot X from the prior 24-bar "day"
    demark_r1  -- R1 = X/2 - L24
    demark_s1  -- S1 = X/2 - H24
    atr        -- Wilder ATR(14) for the risk layer

No lookahead: levels on bar j use bars through j-1 only (the prior
"day" is fully closed before bar j opens).
"""

import numpy as np
import pandas as pd

from strategies import base as B

DAY_BARS = 24  # shipped default: bars per synthetic "day"


def add_indicators(df: pd.DataFrame, day_bars: int = DAY_BARS) -> pd.DataFrame:
    df = df.copy()
    h24 = df["h"].rolling(day_bars, min_periods=day_bars).max().shift(1)
    l24 = df["l"].rolling(day_bars, min_periods=day_bars).min().shift(1)
    c24 = df["c"].shift(day_bars)
    o24 = df["o"].shift(day_bars)
    x = np.where(
        c24 < o24,
        h24 + 2.0 * l24 + c24,
        np.where(
            c24 > o24,
            2.0 * h24 + l24 + c24,
            h24 + l24 + 2.0 * c24,
        ),
    )
    df["demark_x"] = pd.Series(x, index=df.index)
    df["demark_r1"] = df["demark_x"] / 2.0 - l24
    df["demark_s1"] = df["demark_x"] / 2.0 - h24
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
