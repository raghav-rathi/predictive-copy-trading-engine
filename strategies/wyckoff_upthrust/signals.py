"""Wyckoff upthrust signals — SHORT ONLY.

    short_entry -- an upthrust bar (failed breakout above the range);
                   executes at the next bar's open per the harness.
    short_exit  -- close crosses above range_high: the upthrust failed
                   in the other direction — price reclaimed above the
                   range, so the bearish thesis is invalidated.
    long_entry / long_exit -- always False (short-only strategy).

State machine: entries only while flat; the exit cross is only
meaningful while short. Boolean columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    up = df["upthrust"].fillna(False).to_numpy(dtype=bool)
    reclaim = B.crossed_above(df["c"], df["range_high"]).fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "short" and reclaim[i]:
            sx[i] = True
            pos = None
        if pos is None and up[i]:
            se[i] = True
            pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
