"""Swing Failure Pattern signals (Larry Williams, false breakout).

Short entry: price makes a new 20-bar high (high > prior 20-bar high)
             and then closes back below that swing high within the
             next 3 bars (the breakout bar itself counts — a bar that
             pokes above the swing high and closes back below it is
             the canonical failure candle).
Long entry:  mirror — a new 20-bar low, then a close back above that
             swing low within the next 3 bars.
Long exit:   a bearish failure signal (the short-entry condition).
Short exit:  a bullish failure signal (the long-entry condition).

Each breakout arms one pending failure; the first close back inside
consumes it, and an unconfirmed breakout expires after 3 bars. A
newer breakout supersedes a pending one.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies, so
in practice most positions end on the stop/trail/max-hold before the
opposite failure; the opposite failure is the system-defined exit.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import numpy as np
import pandas as pd

LOOKBACK = 20
FAIL_WINDOW = 3


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    low = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    sh = df["swing_high"].to_numpy(dtype=float)
    sl = df["swing_low"].to_numpy(dtype=float)
    n = len(df)
    short_entry = np.zeros(n, dtype=bool)
    long_entry = np.zeros(n, dtype=bool)

    pend_short_level = np.nan
    pend_short_deadline = -1
    pend_long_level = np.nan
    pend_long_deadline = -1
    for i in range(n):
        # Register a new breakout at bar i (supersedes a pending one).
        if not np.isnan(sh[i]) and h[i] > sh[i]:
            pend_short_level = sh[i]
            pend_short_deadline = i + FAIL_WINDOW
        if not np.isnan(sl[i]) and low[i] < sl[i]:
            pend_long_level = sl[i]
            pend_long_deadline = i + FAIL_WINDOW
        # Failure: close back inside the broken level within the window.
        if not np.isnan(pend_short_level) and i <= pend_short_deadline:
            if c[i] < pend_short_level:
                short_entry[i] = True
                pend_short_level = np.nan
        if not np.isnan(pend_long_level) and i <= pend_long_deadline:
            if c[i] > pend_long_level:
                long_entry[i] = True
                pend_long_level = np.nan
        # Expire unconfirmed breakouts.
        if not np.isnan(pend_short_level) and i > pend_short_deadline:
            pend_short_level = np.nan
        if not np.isnan(pend_long_level) and i > pend_long_deadline:
            pend_long_level = np.nan

    df["short_entry"] = short_entry
    df["long_entry"] = long_entry
    df["long_exit"] = short_entry
    df["short_exit"] = long_entry
    return df
