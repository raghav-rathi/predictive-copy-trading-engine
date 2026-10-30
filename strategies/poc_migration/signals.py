"""POC migration signals.

    long_entry  -- POC rose vs 10 bars ago AND close > POC, while flat
    short_entry -- POC fell vs 10 bars ago AND close < POC, while flat
    long_exit   -- POC direction flips (poc_dir == -1) while long
    short_exit  -- POC direction flips (poc_dir == +1) while short

State machine: an exit on a flip bar may be followed by an entry in the
opposite direction on the same bar if that side's entry condition also
holds. Boolean columns, no NaN, no lookahead (POC is causal).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    d = df["poc_dir"].to_numpy(dtype=int)
    poc = df["poc"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and d[i] == -1:
            lx[i] = True
            pos = None
        elif pos == "short" and d[i] == 1:
            sx[i] = True
            pos = None
        if pos is None:
            if d[i] == 1 and np.isfinite(poc[i]) and c[i] > poc[i]:
                le[i] = True
                pos = "long"
            elif d[i] == -1 and np.isfinite(poc[i]) and c[i] < poc[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
