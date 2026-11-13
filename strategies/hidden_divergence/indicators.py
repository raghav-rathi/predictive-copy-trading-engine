"""RSI(14) hidden-divergence indicators.

Swing pivots (5-bar, 2 bars each side):

    swing low  at bar i: low[i] < low[i-1], low[i] < low[i-2],
                        low[i] <= low[i+1], low[i] <= low[i+2]
    swing high at bar i: high[i] > high[i-1], high[i] > high[i-2],
                        high[i] >= high[i+1], high[i] >= high[i+2]

The strict comparison on the left (past) bars and the non-strict
comparison on the right (future) bars keep equal neighbouring
extremes from double-counting as two pivots.

CAUSALITY NOTE: a pivot at bar i is only *confirmed* at bar i+2,
once bars i+1 and i+2 have printed. The ``pivot_low`` / ``pivot_high``
columns mark the pivot bar i itself, but ``signals.add_signals``
only acts on a pivot at bar i+2, so no signal ever uses data beyond
its own bar. The two-bar confirmation lag is the price of using a
centred pivot definition and is documented in CALIBRATION.md.

Columns:

    rsi         -- Wilder RSI(14)
    pivot_low   -- True on a 5-bar swing-low bar
    pivot_high  -- True on a 5-bar swing-high bar
    atr         -- Wilder ATR(14) for the risk layer

No lookahead in the *system*: every signal on bar i uses data through
bar i's close (see the causality note above).
"""

import pandas as pd

from strategies import base as B

RSI_N = 14
PIVOT_LEFT = 2
PIVOT_RIGHT = 2

INDICATOR_COLS = ["rsi", "pivot_low", "pivot_high", "atr"]


def add_indicators(df: pd.DataFrame, rsi_n: int = RSI_N) -> pd.DataFrame:
    df = df.copy()
    low = df["l"]
    high = df["h"]
    pivot_low = (
        (low < low.shift(1))
        & (low < low.shift(2))
        & (low <= low.shift(-1))
        & (low <= low.shift(-2))
    ).fillna(False)
    pivot_high = (
        (high > high.shift(1))
        & (high > high.shift(2))
        & (high >= high.shift(-1))
        & (high >= high.shift(-2))
    ).fillna(False)
    df["rsi"] = B.rsi(df["c"], rsi_n)
    df["pivot_low"] = pivot_low.astype(bool)
    df["pivot_high"] = pivot_high.astype(bool)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
