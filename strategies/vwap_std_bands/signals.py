"""VWAP standard-deviation bands signals.

    long_entry  -- close touched/breached the -2 sigma band on
                   the previous bar (close <= lower_2) and
                   closes back above it on this bar
    short_entry -- mirror at the +2 sigma band
    long_exit   -- close reaches the VWAP midline (close >= vwap)
    short_exit  -- close reaches the VWAP midline (close <= vwap)

State machine: entries only while flat; a midline exit may
be followed by a fresh entry on the same bar only if that
bar also satisfies an entry condition. Boolean columns, no
NaN, no lookahead (all inputs causal).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    lo2 = df["vwap_lower_2"].to_numpy(dtype=float)
    hi2 = df["vwap_upper_2"].to_numpy(dtype=float)
    vw = df["vwap"].to_numpy(dtype=float)

    long_raw = np.zeros(n, dtype=bool)
    short_raw = np.zeros(n, dtype=bool)
    if n >= 2:
        long_raw[1:] = (c[:-1] <= lo2[:-1]) & (c[1:] > lo2[1:])
        short_raw[1:] = (c[:-1] >= hi2[:-1]) & (c[1:] < hi2[1:])
    long_exit_raw = c >= vw
    short_exit_raw = c <= vw

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and long_exit_raw[i]:
            lx[i] = True
            pos = None
        elif pos == "short" and short_exit_raw[i]:
            sx[i] = True
            pos = None
        if pos is None:
            if long_raw[i]:
                le[i] = True
                pos = "long"
            elif short_raw[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
