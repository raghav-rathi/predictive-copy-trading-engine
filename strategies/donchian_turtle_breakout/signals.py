"""Donchian Turtle Breakout (System 1) signals.

LONG on a close above the prior-20-bar Donchian high; SHORT on a
close below the prior-20-bar Donchian low. Exit LONG on a close
below the prior-10-bar Donchian low; exit SHORT on a close above
the prior-10-bar Donchian high. Entries are transition-only: a
signal fires only when flat (or on the same bar an opposite
position exits — a flip — because a close that breaks the 10-bar
exit level can simultaneously break the 20-bar entry level in
the opposite direction). While a position is held, repeated
breakout bars do NOT re-enter (no pyramiding; the harness also
enforces one position at a time).

All conditions read bar-i values at bar i; signal columns are
boolean, no NaN, no lookahead. Execution is at bar i+1's open
per the house convention.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    long_br = df["long_breakout"].fillna(False).to_numpy(dtype=bool)
    short_br = df["short_breakout"].fillna(False).to_numpy(dtype=bool)
    long_x = df["long_exit_cond"].fillna(False).to_numpy(dtype=bool)
    short_x = df["short_exit_cond"].fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short" / None
    for i in range(n):
        if pos == "long":
            if long_x[i]:
                lx[i] = True
                pos = None
        elif pos == "short":
            if short_x[i]:
                sx[i] = True
                pos = None
        if pos is None:
            if long_br[i]:
                le[i] = True
                pos = "long"
            elif short_br[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
