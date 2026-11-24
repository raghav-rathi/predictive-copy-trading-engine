"""Gap-fill fade signals.

Mean reversion on 1h gaps: fade the gap, expecting price to
fill back to the prior bar's close.

LONG when a gap down fired on bar i (gap < -0.5 * ATR(14)) —
buy the dip, expecting a fill back up toward prev_close.
SHORT is the mirror on a gap up (gap > +0.5 * ATR(14)).

Only ONE fade per gap: the signal fires once, on the gap bar
itself. While a position is held, further gap bars do NOT
re-enter (state machine, transition-only entries).

Exits (state machine, one pass; the fill level is captured at
entry — the prev_close of the gap bar):
- Long: close >= fill_level (the gap is filled), OR an
  opposite gap signal (gap_up) fires.
- Short: close <= fill_level, OR an opposite gap signal
  (gap_dn) fires.
- A fill that already happened on the gap bar itself does NOT
  exit the trade: the position only exists from the next bar's
  open (execution at bar i+1's open), so fill exits are checked
  from the bar after entry onward.
- An exit on a bar that also carries the opposite gap signal
  flips the position (exit + entry on the same bar).

The risk layer (2xATR stop, 24-bar max hold) also applies via
the harness. No target — the fill exit is the target. All
conditions read bar-i values at bar i; signal columns are
boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    gap_up = df["gap_up"].fillna(False).to_numpy(dtype=bool)
    gap_dn = df["gap_dn"].fillna(False).to_numpy(dtype=bool)
    fill_level = df["fill_level"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short" / None
    fill = np.nan
    for i in range(n):
        if pos == "long":
            if c[i] >= fill or gap_up[i]:
                lx[i] = True
                pos = None
                fill = np.nan
        elif pos == "short":
            if c[i] <= fill or gap_dn[i]:
                sx[i] = True
                pos = None
                fill = np.nan
        if pos is None:
            if gap_dn[i]:
                le[i] = True
                pos = "long"
                fill = fill_level[i]
            elif gap_up[i]:
                se[i] = True
                pos = "short"
                fill = fill_level[i]

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
