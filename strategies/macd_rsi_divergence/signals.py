"""MACD divergence signals (MACD-only, both sides).

LONG on the confirmation bar of a bullish regular divergence
(lower confirmed pivot low, higher MACD histogram at the pivot
than at the previous pivot low) AND the histogram rising on
that bar (``hist[i] > hist[i-1]``). SHORT is the mirror
(bearish divergence AND histogram falling).

Exits (state machine, one pass):
- Long: MACD histogram crosses below zero
  (``hist[i] < 0`` and ``hist[i-1] >= 0``), OR a new bearish
  divergence is confirmed.
- Short: histogram crosses above zero, OR a new bullish
  divergence is confirmed.
- An exit on a bar that also carries the opposite entry
  condition flips the position (exit + entry on the same bar).

Entries are transition-only: a signal fires only when flat (or
on a flip bar). While a position is held, repeated divergence
bars do NOT re-enter. Divergence needs two pivots by
construction, so entries lag the turn by design (see README).

All conditions read bar-i values at bar i; signal columns are
boolean, no NaN, no lookahead. Execution is at bar i+1's open
per the house convention.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    hist = df["macd_hist"].fillna(0.0).to_numpy(dtype=float)
    bull = df["bullish_divergence"].fillna(False).to_numpy(dtype=bool)
    bear = df["bearish_divergence"].fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short" / None
    for i in range(n):
        hist_rising = i > 0 and hist[i] > hist[i - 1]
        hist_falling = i > 0 and hist[i] < hist[i - 1]
        cross_below_zero = i > 0 and hist[i] < 0 and hist[i - 1] >= 0
        cross_above_zero = i > 0 and hist[i] > 0 and hist[i - 1] <= 0
        if pos == "long":
            if cross_below_zero or bear[i]:
                lx[i] = True
                pos = None
        elif pos == "short":
            if cross_above_zero or bull[i]:
                sx[i] = True
                pos = None
        if pos is None:
            if bull[i] and hist_rising:
                le[i] = True
                pos = "long"
            elif bear[i] and hist_falling:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
