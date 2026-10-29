"""Stochastic Pop signals.

    long_entry  -- pop_up bar (fastK crosses above 80 with a
                   20-bar-high breakout) while flat
    short_entry -- pop_dn bar (fastK crosses below 20 with a
                   20-bar-low breakdown) while flat
    long_exit   -- fastK crosses back below 80 (the pop is spent)
    short_exit  -- fastK crosses back above 20

Pops are fast: the exit is the oscillator leaving the extreme
zone, not a reversal signal. The risk layer (tight 1.5xATR stop,
72-bar max hold) does the rest. Boolean columns, no NaN, no
lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    k = df["fastK"]
    pop_up = df["pop_up"].to_numpy(dtype=bool)
    pop_dn = df["pop_dn"].to_numpy(dtype=bool)
    exit_long = B.crossed_below(k, 80.0).fillna(False).to_numpy(dtype=bool)
    exit_short = B.crossed_above(k, 20.0).fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and exit_long[i]:
            lx[i] = True
            pos = None
        elif pos == "short" and exit_short[i]:
            sx[i] = True
            pos = None
        if pos is None:
            if pop_up[i]:
                le[i] = True
                pos = "long"
            elif pop_dn[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
