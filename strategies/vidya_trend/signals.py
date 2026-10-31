"""VIDYA trend signals.

    long_entry  -- close crosses above VIDYA
    short_entry -- close crosses below VIDYA
    long_exit   -- opposite cross (close below VIDYA)
    short_exit  -- opposite cross (close above VIDYA)

A cross bar both exits the open side and enters the other side, in the
same position-state-machine pattern as the template strategy. Boolean
columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    cross_up = B.crossed_above(df["c"], df["vidya"]).fillna(False).to_numpy(dtype=bool)
    cross_down = B.crossed_below(df["c"], df["vidya"]).fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and cross_down[i]:
            lx[i] = True
            pos = None
        elif pos == "short" and cross_up[i]:
            sx[i] = True
            pos = None
        if pos is None:
            if cross_up[i]:
                le[i] = True
                pos = "long"
            elif cross_down[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
