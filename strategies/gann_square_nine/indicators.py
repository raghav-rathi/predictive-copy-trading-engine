"""Gann Square of Nine level indicators.

For the prior close p, s = sqrt(p), base = floor(s * 4) / 4 (the
quarter-root grid line at or below s). The 45-degree ladder is
L_j = (base + 0.25 * j)^2, j = 0..8, i.e. each step adds 0.25 to the
square root (45 degrees; a full 360-degree turn adds 2.0). The level
immediately above the prior close is L_1 (L_0 <= p < L_1, except on
the measure-zero exact-grid case where L_0 == p) and the level at or
below it is L_0. next_up / next_down are one further 45-degree step
beyond those levels. All levels on bar i are computed from bar i-1's
close only, so no lookahead.
"""

import numpy as np
import pandas as pd

INDICATOR_COLS = [
    "gann_level_above",
    "gann_level_below",
    "gann_next_up",
    "gann_next_down",
    "gann_dist_above_pct",
    "gann_dist_below_pct",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_c = df["c"].shift(1)
    s = np.sqrt(prev_c)
    base = np.floor(s * 4) / 4
    level_above = (base + 0.25) ** 2
    level_below = base**2
    next_up = (base + 0.5) ** 2
    next_down = np.where(base >= 0.25, (base - 0.25) ** 2, np.nan)
    df["gann_level_above"] = level_above
    df["gann_level_below"] = level_below
    df["gann_next_up"] = next_up
    df["gann_next_down"] = next_down
    df["gann_dist_above_pct"] = (level_above - prev_c) / prev_c
    df["gann_dist_below_pct"] = (prev_c - level_below) / prev_c
    return df
