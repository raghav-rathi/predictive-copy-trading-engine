"""Triple top/bottom signals.

    long_entry  -- confirmed triple bottom bar (triple_dir == +1)
    short_entry -- confirmed triple top bar (triple_dir == -1)
    long_exit   -- a triple top bar while long (opposite pattern)
    short_exit  -- a triple bottom bar while short

State machine: entries only while flat, exits only from the
matching position; an opposite pattern can exit one side and
enter the other on the same bar. Boolean columns, no NaN, no
lookahead (triple_dir is already lagged at the indicator level).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    d = df["triple_dir"].to_numpy(dtype=int)

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
