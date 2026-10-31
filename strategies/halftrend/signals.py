"""HalfTrend signals.

    long_entry  -- HalfTrend trend flips 1 (down) -> 0 (up)
    short_entry -- HalfTrend trend flips 0 (up) -> 1 (down)
    long_exit   -- opposite flip (0 -> 1)
    short_exit  -- opposite flip (1 -> 0)

A flip bar both exits the open side and enters the other side, in the
same position-state-machine pattern as the template strategy. Boolean
columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    tr = df["ht_trend"].to_numpy(dtype=int)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        flip_up = i > 0 and tr[i] == 0 and tr[i - 1] == 1
        flip_down = i > 0 and tr[i] == 1 and tr[i - 1] == 0
        if pos == "long" and flip_down:
            lx[i] = True
            pos = None
        elif pos == "short" and flip_up:
            sx[i] = True
            pos = None
        if pos is None:
            if flip_up:
                le[i] = True
                pos = "long"
            elif flip_down:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
