"""Gap-fill fade indicators (causal, no lookahead).

A gap is the difference between bar i's open and bar i-1's
close:
- prev_close = c.shift(1) (bar i-1's close — known by bar i).
- gap = o - prev_close.
- gap_atr = |gap| / ATR(14), with ATR(14) taken at bar i
  (Wilder ATR through bar i's close; the signal is evaluated
  at bar i's close, so this is causal).
- gap_up = gap > 0.5 * ATR(14); gap_dn = gap < -0.5 * ATR(14).
  Strict inequalities: a gap of exactly 0.5 ATR is NOT a gap
  signal (boundary test in test_gap_fill_fade.py).
- fill_level = prev_close — the price a fade expects to return
  to (the prior bar's close).

The gap is visible at bar i's open, hence known by bar i's
close; the signal fires on bar i and executes at bar i+1's
open per the house convention.

Seeding: prev_close is NaN on bar 0 (no prior close); gap and
gap_atr are seeded to 0.0 there and fill_level is seeded to
bar 0's own close, so no indicator column used by a signal
carries NaN. ATR(14) itself is NaN for the first 13 bars and
is kept as computed in ``atr14``; gap_atr is 0.0 wherever ATR
is not yet defined, so no gap can fire in the seeding window.
WARMUP = 30 covers it.
"""

import numpy as np
import pandas as pd

from strategies import base as B

GAP_ATR_MULT = 0.5


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l, o = df["c"], df["h"], df["l"], df["o"]

    prev_close = c.shift(1)
    df["prev_close"] = prev_close
    gap = (o - prev_close).fillna(0.0)
    df["gap"] = gap
    atr14 = B.atr(h, l, c, 14)
    df["atr14"] = atr14
    gap_atr = (gap.abs() / atr14).fillna(0.0)
    df["gap_atr"] = gap_atr
    # Raw atr14 (NaN while seeding): comparisons against NaN are
    # False, so no gap can fire before ATR is defined.
    df["gap_up"] = gap > GAP_ATR_MULT * atr14
    df["gap_dn"] = gap < -GAP_ATR_MULT * atr14
    df["fill_level"] = prev_close.fillna(c)
    return df
