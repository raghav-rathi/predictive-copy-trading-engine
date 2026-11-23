"""Tillson T3 signals.

LONG when C > T3(10, 0.7) AND T3(10) rising AND T3(10) > T3(30, 0.7)
(the slow T3 agrees); SHORT on the mirror. Entries are
transitions only: a state machine tracks the open position, so a
setup that stays true for twenty bars enters once, not twenty
times. The harness executes at the next bar's open.

Exits (state machine, one pass):
- Long: close back through T3(10) (C < T3) OR T3(10) turns down.
- Short: close back through T3(10) (C > T3) OR T3(10) turns up.
- An opposite setup on the same bar as an exit flips the position
  (exit + entry on the same bar).

All conditions read bar-i values at bar i; signal columns are
boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    t3 = df["t3_fast"].to_numpy(dtype=float)
    rising = df["t3_rising"].fillna(False).to_numpy(dtype=bool)
    falling = df["t3_falling"].fillna(False).to_numpy(dtype=bool)
    long_setup = df["long_setup"].fillna(False).to_numpy(dtype=bool)
    short_setup = df["short_setup"].fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short"
    for i in range(n):
        if pos == "long":
            if c[i] < t3[i] or falling[i]:
                lx[i] = True
                pos = None
        elif pos == "short":
            if c[i] > t3[i] or rising[i]:
                sx[i] = True
                pos = None
        if pos is None:
            if long_setup[i]:
                le[i] = True
                pos = "long"
            elif short_setup[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
