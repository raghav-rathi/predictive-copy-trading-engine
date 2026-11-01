"""NR7 breakout signals.

    long_entry  -- close crosses above the live NR7 bar's high
    short_entry -- close crosses below the live NR7 bar's low
    long_exit   -- close crosses below the live NR7 bar's low
                  (breakout failed)
    short_exit  -- close crosses above the live NR7 bar's high

The level series only changes at new NR7 bars, so a cross is always
measured against the setup's own level. Boolean columns, no NaN,
no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    hi = df["nr7_high"].to_numpy(dtype=float)
    lo = df["nr7_low"].to_numpy(dtype=float)
    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)
    for i in range(1, n):
        if not np.isnan(hi[i]):
            if c[i] > hi[i] and c[i - 1] <= hi[i]:
                le[i] = True
            if c[i] > hi[i] and c[i - 1] <= hi[i]:
                sx[i] = True
        if not np.isnan(lo[i]):
            if c[i] < lo[i] and c[i - 1] >= lo[i]:
                se[i] = True
            if c[i] < lo[i] and c[i - 1] >= lo[i]:
                lx[i] = True
    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
