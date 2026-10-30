"""Liquidity sweep + reclaim indicators (causal, no lookahead).

Reference levels are the prior 20 bars (excluding the current
bar): ``sweep_low_level`` is the minimum low of bars i-20..i-1,
``sweep_high_level`` the maximum high of the same window. A
sweep is a bar whose low wicks below the prior 20-bar swing low
(or high wicks above the prior 20-bar swing high). A reclaim
closes back inside the range: close above the swept low (or
below the swept high).

``sweep_dir`` fires +1 (long setup) when a low sweep is
reclaimed on the sweep bar itself or on the next bar — the
next-bar case requires that the sweep bar did NOT already
reclaim, so one sweep fires at most once. Mirror for -1.
A close that stays beyond the level is a breakdown, not a
sweep, and never fires.

Columns:
    sweep_low_level, sweep_high_level -- prior-20-bar levels
    sweep_dir -- +1 on a reclaimed low sweep, -1 on a reclaimed
                 high sweep, else 0
    atr        -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

LOOKBACK = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)

    # Prior-20-bar levels, excluding the current bar (shift by 1
    # after the rolling window so no current-bar information leaks).
    low_series = pd.Series(l)
    high_series = pd.Series(h)
    low_level = low_series.rolling(LOOKBACK, min_periods=LOOKBACK).min().shift(1).to_numpy(dtype=float)
    high_level = high_series.rolling(LOOKBACK, min_periods=LOOKBACK).max().shift(1).to_numpy(dtype=float)

    wick_low = np.zeros(n, dtype=bool)
    wick_high = np.zeros(n, dtype=bool)
    for i in range(n):
        if np.isfinite(low_level[i]) and l[i] < low_level[i]:
            wick_low[i] = True
        if np.isfinite(high_level[i]) and h[i] > high_level[i]:
            wick_high[i] = True

    sweep_dir = np.zeros(n, dtype=int)
    for i in range(n):
        # Reclaim on the sweep bar itself.
        if wick_low[i] and c[i] > low_level[i]:
            sweep_dir[i] = 1
        elif wick_high[i] and c[i] < high_level[i]:
            sweep_dir[i] = -1
        # Reclaim on the next bar, only if the sweep bar did not
        # already reclaim (avoids double-firing one sweep).
        elif i > 0 and wick_low[i - 1] and c[i - 1] <= low_level[i - 1] and c[i] > low_level[i - 1]:
            sweep_dir[i] = 1
        elif i > 0 and wick_high[i - 1] and c[i - 1] >= high_level[i - 1] and c[i] < high_level[i - 1]:
            sweep_dir[i] = -1

    df["sweep_low_level"] = low_level
    df["sweep_high_level"] = high_level
    df["sweep_dir"] = sweep_dir
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
