"""Fibonacci retracement signals.

Long: an uptrend swing's pullback has touched the 38.2%-61.8% golden
zone; enter on the close of the first green candle that closes in or
above the zone (close >= zone_lo), once per swing, and only while the
close is still between A (invalidation) and B (target). Exit long at a
close >= B (the old high) or a close below A (setup invalidated).
Short is the mirror image: first red candle closing in or below the
zone, exit at a close <= B or above A. Entry/exit levels are latched
at entry so the trade's levels survive the swing clearing or being
replaced.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    o = df["o"].to_numpy()
    c = df["c"].to_numpy()
    direction = df["fib_dir"].to_numpy()
    a_col = df["fib_a"].to_numpy()
    b_col = df["fib_b"].to_numpy()
    zlo = df["fib_zone_lo"].to_numpy()
    zhi = df["fib_zone_hi"].to_numpy()
    touched = df["fib_touched"].to_numpy()
    swing_id = df["fib_swing_id"].to_numpy()
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    entered: set[int] = set()
    latched_long = None   # (a, b) of the entered long swing
    latched_short = None  # (a, b) of the entered short swing
    for i in range(n):
        sid = int(swing_id[i]) if np.isfinite(swing_id[i]) else None
        if (
            direction[i] == 1.0
            and touched[i] == 1.0
            and sid is not None
            and sid not in entered
            and c[i] > o[i]
            and np.isfinite(zlo[i])
            and c[i] >= zlo[i]
            and np.isfinite(a_col[i])
            and c[i] >= a_col[i]
            and np.isfinite(b_col[i])
            and c[i] < b_col[i]
        ):
            long_entry[i] = True
            entered.add(sid)
            latched_long = (float(a_col[i]), float(b_col[i]))
        elif (
            direction[i] == -1.0
            and touched[i] == 1.0
            and sid is not None
            and sid not in entered
            and c[i] < o[i]
            and np.isfinite(zhi[i])
            and c[i] <= zhi[i]
            and np.isfinite(a_col[i])
            and c[i] <= a_col[i]
            and np.isfinite(b_col[i])
            and c[i] > b_col[i]
        ):
            short_entry[i] = True
            entered.add(sid)
            latched_short = (float(a_col[i]), float(b_col[i]))
        if latched_long is not None and (c[i] >= latched_long[1] or c[i] < latched_long[0]):
            long_exit[i] = True
            latched_long = None
        if latched_short is not None and (c[i] <= latched_short[1] or c[i] > latched_short[0]):
            short_exit[i] = True
            latched_short = None
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
