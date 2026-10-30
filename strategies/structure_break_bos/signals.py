"""Structure-break BOS signals.

    long_entry  -- BOS-continuation up (bos_dir == +1) while flat
    short_entry -- BOS-continuation down (bos_dir == -1) while flat
    long_exit   -- opposite structure break (break_down) while long
    short_exit  -- opposite structure break (break_up) while short

An opposite break exits even when it is only the first break in
its direction (it sets the new trend state but, per the entry
rule, does not itself enter). Boolean columns, no NaN, no
lookahead (all inputs are already causal).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    d = df["bos_dir"].to_numpy(dtype=int)
    bu = df["break_up"].to_numpy(dtype=bool)
    bd = df["break_down"].to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and bd[i]:
            lx[i] = True
            pos = None
        elif pos == "short" and bu[i]:
            sx[i] = True
            pos = None
        if pos is None:
            if d[i] == 1:
                le[i] = True
                pos = "long"
            elif d[i] == -1:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
