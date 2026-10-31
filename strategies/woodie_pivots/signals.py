"""Woodie pivot signals.

    long_entry  -- close crosses above prior-day R1
    short_entry -- close crosses below prior-day S1
    long_exit   -- close crosses below prior-day PP
    short_exit  -- close crosses above prior-day PP

State machine: entries only while flat; an exit may be followed by
an opposite entry on the same bar if that bar also crosses the
opposite trigger. Boolean columns, no NaN, no lookahead (levels are
prior-day only, and a cross on bar i uses only closes through i).
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"]
    cross_r1 = B.crossed_above(c, df["r1"]).fillna(False).to_numpy(dtype=bool)
    cross_s1 = B.crossed_below(c, df["s1"]).fillna(False).to_numpy(dtype=bool)
    cross_pp_dn = B.crossed_below(c, df["pp"]).fillna(False).to_numpy(dtype=bool)
    cross_pp_up = B.crossed_above(c, df["pp"]).fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and cross_pp_dn[i]:
            lx[i] = True
            pos = None
        elif pos == "short" and cross_pp_up[i]:
            sx[i] = True
            pos = None
        if pos is None:
            if cross_r1[i]:
                le[i] = True
                pos = "long"
            elif cross_s1[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
