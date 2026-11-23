"""Fisher Transform trend signals.

LONG when the smoothed Fisher Transform crosses above 0 from
below and is rising; SHORT on the mirror cross below 0 while
falling. The 0-cross is the trigger (the Fisher Transform is a
near-Gaussianization of price, not a momentum oscillator — the
cross marks the normalized price position flipping from the
lower to the upper half of its 10-bar range).

Exits (state machine, one pass):
- Long: Fisher crosses back below 0, OR Fisher turns down two
  bars in a row (fisher[i] < fisher[i-1] < fisher[i-2]).
- Short: mirror — cross back above 0, or two consecutive up bars.
- A cross back through 0 while in a position flips it: the exit
  and the opposite entry fire on the same bar (the cross is both
  an exit and a fresh entry trigger). A two-bar-turn exit does
  NOT flip — it only closes the position.

All conditions read bar-i values at bar i; signal columns are
boolean, no NaN, no lookahead. Entries are transition-only:
a position is opened only on the cross bar, never re-entered
while already holding the same side.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    f = df["fisher"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" | "short" | None
    for i in range(n):
        if i == 0:
            # No previous bar, so no cross can be defined at bar 0.
            continue
        if i == 1:
            prev = f[0]
            prev2 = 0.0
        else:
            prev = f[i - 1]
            prev2 = f[i - 2]
        rising = f[i] > prev
        falling = f[i] < prev
        cross_up = f[i] > 0.0 and prev <= 0.0
        cross_dn = f[i] < 0.0 and prev >= 0.0
        two_down = f[i] < prev and prev < prev2
        two_up = f[i] > prev and prev > prev2

        if pos == "long":
            if cross_dn:
                lx[i] = True
                if falling:  # cross down implies falling; flip short
                    se[i] = True
                    pos = "short"
                else:
                    pos = None
            elif two_down:
                lx[i] = True
                pos = None
        elif pos == "short":
            if cross_up:
                sx[i] = True
                if rising:  # cross up implies rising; flip long
                    le[i] = True
                    pos = "long"
                else:
                    pos = None
            elif two_up:
                sx[i] = True
                pos = None

        if pos is None:
            if cross_up and rising:
                le[i] = True
                pos = "long"
            elif cross_dn and falling:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
