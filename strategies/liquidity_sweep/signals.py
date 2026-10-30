"""Liquidity sweep signals.

    long_entry  -- reclaimed low sweep (sweep_dir == +1) while flat
    short_entry -- reclaimed high sweep (sweep_dir == -1) while flat
    long_exit   -- opposite sweep signal (sweep_dir == -1) while long
    short_exit  -- opposite sweep signal (sweep_dir == +1) while short

The risk layer's trailing stop is the other exit path.
Boolean columns, no NaN, no lookahead (sweep_dir is causal).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    d = df["sweep_dir"].to_numpy(dtype=int)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        di = int(d[i])
        if pos == "long" and di == -1:
            lx[i] = True
            pos = None
        elif pos == "short" and di == 1:
            sx[i] = True
            pos = None
        if pos is None:
            if di == 1:
                le[i] = True
                pos = "long"
            elif di == -1:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
