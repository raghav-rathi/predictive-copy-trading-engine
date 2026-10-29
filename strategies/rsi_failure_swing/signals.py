"""RSI failure-swing signals.

    long_entry  -- bullish failure-swing trigger bar (rsi_fs_dir
                   == +1) while flat
    short_entry -- bearish failure-swing trigger bar (rsi_fs_dir
                   == -1) while flat
    long_exit   -- a bearish failure-swing bar while long
    short_exit  -- a bullish failure-swing bar while short

State machine: entries only while flat; an opposite trigger exits
one side and may enter the other on the same bar. Boolean columns,
no NaN, no lookahead (rsi_fs_dir is already lagged at the
indicator level).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    d = df["rsi_fs_dir"].to_numpy(dtype=int)

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
