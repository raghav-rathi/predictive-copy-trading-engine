"""Triple-EMA stack signals.

    long_entry  -- bull-stacked while flat
    short_entry -- bear-stacked while flat
    long_exit   -- stack is no longer bull (unstacked) while long
    short_exit  -- stack is no longer bear (unstacked) while short

State machine: entries only while flat; an unstack exits one
side and may enter the other on the same bar. Boolean columns,
no NaN, no lookahead (stacks use only closes through bar i).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    bull = df["bull_stack"].fillna(False).to_numpy(dtype=bool)
    bear = df["bear_stack"].fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and not bull[i]:
            lx[i] = True
            pos = None
        elif pos == "short" and not bear[i]:
            sx[i] = True
            pos = None
        if pos is None:
            if bull[i]:
                le[i] = True
                pos = "long"
            elif bear[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
