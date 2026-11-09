"""Gann Square of Nine signals.

Long: the close crosses above the nearest Square-of-Nine level above
the prior close (gann_level_above, built from the prior close) and
that level sits within 0.5% of the prior close. Short: mirror — the
close crosses below the nearest level below the prior close and that
level sits within 0.5% of the prior close. Exit a long when the close
falls back below the entry level or reaches the next level up
(gann_next_up at the entry bar); exit a short when the close rises
back above the entry level or reaches the next level down.

The entry level / target are entry-bar state, so the signal loop
tracks the open side causally (bar i's signals use only data through
bar i's close). Entries only fire while flat; the backtest harness
holds one position at a time anyway.
"""

import numpy as np
import pandas as pd

MAX_DIST_PCT = 0.005


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    above = df["gann_level_above"].to_numpy(dtype=float)
    below = df["gann_level_below"].to_numpy(dtype=float)
    next_up = df["gann_next_up"].to_numpy(dtype=float)
    next_down = df["gann_next_down"].to_numpy(dtype=float)
    prev = np.concatenate([[np.nan], c[:-1]]) if len(c) else np.array([])
    n = len(df)
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    state = 0  # 0 flat, 1 long, -1 short
    entry_level = np.nan
    target = np.nan
    for i in range(n):
        if np.isnan(above[i]) or np.isnan(below[i]) or np.isnan(prev[i]):
            continue
        if state == 0:
            if c[i] > above[i] and (above[i] - prev[i]) / prev[i] <= MAX_DIST_PCT:
                long_entry[i] = True
                state = 1
                entry_level = above[i]
                target = next_up[i]
            elif c[i] < below[i] and (prev[i] - below[i]) / prev[i] <= MAX_DIST_PCT:
                short_entry[i] = True
                state = -1
                entry_level = below[i]
                target = next_down[i]
        elif state == 1:
            if c[i] < entry_level or (not np.isnan(target) and c[i] >= target):
                long_exit[i] = True
                state = 0
                entry_level = np.nan
                target = np.nan
        else:  # state == -1
            if c[i] > entry_level or (not np.isnan(target) and c[i] <= target):
                short_exit[i] = True
                state = 0
                entry_level = np.nan
                target = np.nan
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
