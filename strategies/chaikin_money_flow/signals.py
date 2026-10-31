"""Chaikin Money Flow zero-cross signals.

    long_entry  -- CMF(20) crosses above 0 (accumulation takes over)
    short_entry -- CMF(20) crosses below 0 (distribution takes over)
    long_exit   -- CMF(20) crosses below 0 (opposite cross)
    short_exit  -- CMF(20) crosses above 0 (opposite cross)

State machine: entries only while flat; an opposite cross exits and may
re-enter the other side on the same bar. Boolean columns, no NaN, no
lookahead. A signal on bar i executes at bar i+1's open (harness).
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    cross_up = B.crossed_above(df["cmf"], 0).fillna(False).to_numpy(dtype=bool)
    cross_down = B.crossed_below(df["cmf"], 0).fillna(False).to_numpy(dtype=bool)

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
