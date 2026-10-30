"""Point & Figure signals.

    long_entry  -- double-top breakout (pf_signal == +1) while flat
    short_entry -- double-bottom breakdown (pf_signal == -1) while flat
    long_exit   -- column flips to O (pf_reversal and pf_dir == -1)
    short_exit  -- column flips to X (pf_reversal and pf_dir == +1)

State machine: entries only while flat; a flip exits one side and may
enter the other on the same bar if that bar also carries the opposite
breakout signal. Boolean columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    sig = df["pf_signal"].to_numpy(dtype=int)
    rev = df["pf_reversal"].to_numpy(dtype=bool)
    d = df["pf_dir"].to_numpy(dtype=int)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and rev[i] and d[i] == -1:
            lx[i] = True
            pos = None
        elif pos == "short" and rev[i] and d[i] == 1:
            sx[i] = True
            pos = None
        if pos is None:
            if sig[i] == 1:
                le[i] = True
                pos = "long"
            elif sig[i] == -1:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
