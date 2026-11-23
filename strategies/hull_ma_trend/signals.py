"""Hull MA trend signals.

LONG when C > HMA(16) AND HMA(16) rising AND C > HMA(64); SHORT on
the mirror. Entries are transitions only: a state machine tracks
the open position, so a setup that stays true for twenty bars
enters once, not twenty times. The harness executes at the next
bar's open.

Exits (state machine, one pass):
- Long: close below HMA(16) OR HMA(16) turns down (falling).
- Short: close above HMA(16) OR HMA(16) turns up (rising).
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
    hma16 = df["hma16"].to_numpy(dtype=float)
    rising = df["hma16_rising"].fillna(False).to_numpy(dtype=bool)
    falling = df["hma16_falling"].fillna(False).to_numpy(dtype=bool)
    long_setup = df["long_setup"].fillna(False).to_numpy(dtype=bool)
    short_setup = df["short_setup"].fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short"
    for i in range(n):
        if pos == "long":
            if c[i] < hma16[i] or falling[i]:
                lx[i] = True
                pos = None
        elif pos == "short":
            if c[i] > hma16[i] or rising[i]:
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
