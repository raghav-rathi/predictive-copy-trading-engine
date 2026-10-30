"""Order-flow imbalance signals.

    long_entry  -- imbalance crosses above +0.25 while close >
                   EMA(20)
    short_entry -- imbalance crosses below -0.25 while close <
                   EMA(20)
    long_exit   -- imbalance crosses back through 0 (below)
    short_exit  -- imbalance crosses back through 0 (above)

Crosses use the previous bar's imbalance, with NaN treated
as no cross (comparisons against NaN are False), so the
first WINDOW-1 bars can never signal. State machine: entries
only while flat; a zero-cross exit may be followed by a
fresh entry on the same bar only if that bar also satisfies
an entry condition. Boolean columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B

LONG_THRESH = 0.25
SHORT_THRESH = -0.25


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    imb = df["imbalance"]
    c = df["c"].to_numpy(dtype=float)
    ema = df["ema20"].to_numpy(dtype=float)

    cross_up = B.crossed_above(imb, LONG_THRESH).to_numpy(dtype=bool)
    cross_dn = B.crossed_below(imb, SHORT_THRESH).to_numpy(dtype=bool)
    exit_long = B.crossed_below(imb, 0.0).to_numpy(dtype=bool)
    exit_short = B.crossed_above(imb, 0.0).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and exit_long[i]:
            lx[i] = True
            pos = None
        elif pos == "short" and exit_short[i]:
            sx[i] = True
            pos = None
        if pos is None:
            if cross_up[i] and c[i] > ema[i]:
                le[i] = True
                pos = "long"
            elif cross_dn[i] and c[i] < ema[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
