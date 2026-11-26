"""Williams %R divergence signals (state machine, one pass).

LONG on the confirmation bar of a bullish regular divergence
(lower confirmed pivot low, higher %R at the pivot than at
the previous pivot low, %R < -80 at the pivot). SHORT is the
mirror (bearish divergence, %R > -20 at the pivot).

Exits (state machine, one pass):
- Long: %R crosses below -50 (``wr[i] < -50`` and
  ``wr[i-1] >= -50``), OR a new bearish divergence is
  confirmed.
- Short: %R crosses above -50, OR a new bullish divergence
  is confirmed.
- An exit on a bar that also carries the opposite entry
  condition flips the position (exit + entry on the same bar).

Entries are transition-only: a signal fires only when flat
(or on a flip bar). While a position is held, repeated
divergence bars do NOT re-enter. Divergence needs two pivots
by construction, so entries lag the turn by design (see
README).

All conditions read bar-i values at bar i; signal columns
are boolean, no NaN, no lookahead. Execution is at bar i+1's
open per the house convention. %R is seeded to -50 where the
indicator is NaN (pre-warmup), the neutral value consistent
with the flat-range convention in indicators.py.
"""

import numpy as np
import pandas as pd

from strategies.base import crossed_above, crossed_below

EXIT_LEVEL = -50.0


def add_signals(
    df: pd.DataFrame,
    exit_level: float = EXIT_LEVEL,
) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    wr = df["williams_r"].fillna(-50.0).to_numpy(dtype=float)
    bull = df["bullish_divergence"].fillna(False).to_numpy(dtype=bool)
    bear = df["bearish_divergence"].fillna(False).to_numpy(dtype=bool)
    cross_below = crossed_below(
        pd.Series(wr, index=df.index), exit_level
    ).to_numpy(dtype=bool)
    cross_above = crossed_above(
        pd.Series(wr, index=df.index), exit_level
    ).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short" / None
    for i in range(n):
        if pos == "long":
            if cross_below[i] or bear[i]:
                lx[i] = True
                pos = None
        elif pos == "short":
            if cross_above[i] or bull[i]:
                sx[i] = True
                pos = None
        if pos is None:
            if bull[i]:
                le[i] = True
                pos = "long"
            elif bear[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
