"""Instantaneous Trendline signals.

LONG when price is above the Instantaneous Trendline AND the
trendline is rising (IT[i] > IT[i-1]); SHORT on the mirror
(C < IT and IT falling). Entries are transition-only: a position
opens only on the bar where the condition first becomes true
(after being false the prior bar), never re-entered while the
condition merely persists.

Exits (state machine, one pass):
- Long: close back through the trendline (C <= IT), OR the
  trendline turns against the position (IT[i] < IT[i-1]).
- Short: mirror — C >= IT, or IT[i] > IT[i-1].
- An opposite-side transition while in a position flips it:
  the exit and the opposite entry fire on the same bar. A
  plain exit (no opposite transition) only closes the position.

All conditions read bar-i values at bar i; signal columns are
boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    it = df["it"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" | "short" | None
    prev_long = False
    prev_short = False
    for i in range(n):
        if i == 0:
            long_cond = False
            short_cond = False
        else:
            rising = it[i] > it[i - 1]
            falling = it[i] < it[i - 1]
            long_cond = c[i] > it[i] and rising
            short_cond = c[i] < it[i] and falling

        if pos == "long":
            if short_cond and not prev_short:
                lx[i] = True
                se[i] = True
                pos = "short"
            elif c[i] <= it[i] or it[i] < it[i - 1]:
                lx[i] = True
                pos = None
        elif pos == "short":
            if long_cond and not prev_long:
                sx[i] = True
                le[i] = True
                pos = "long"
            elif c[i] >= it[i] or it[i] > it[i - 1]:
                sx[i] = True
                pos = None

        if pos is None:
            if long_cond and not prev_long:
                le[i] = True
                pos = "long"
            elif short_cond and not prev_short:
                se[i] = True
                pos = "short"

        prev_long = long_cond
        prev_short = short_cond

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
