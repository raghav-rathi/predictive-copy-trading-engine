"""Grid trading indicators (classic range grid).

The trailing N-bar (default 200) high/low range is split into LEVELS
(default 10) equal levels:

    grid_high = highest high over N bars
    grid_low  = lowest low over N bars
    grid_step = (grid_high - grid_low) / LEVELS
    grid_mid  = (grid_high + grid_low) / 2
    grid_pos  = (close - grid_low) / (grid_high - grid_low)

grid_pos is the close's position in the range: 0 at the range low,
1 at the range high. The grid is recomputed causally each bar from
the trailing N bars (including the current bar, which is known at
the close).

Columns:

    grid_high, grid_low -- trailing range extremes
    grid_range          -- grid_high - grid_low
    grid_step           -- range / LEVELS
    grid_mid            -- range midpoint
    grid_pos            -- close position in [0, 1] (NaN on zero range)
    atr                 -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
A zero range yields grid_pos NaN (no signal) rather than a
division-by-zero blow-up.
"""

import numpy as np
import pandas as pd

from strategies import base as B

GRID_N = 200
LEVELS = 10
BOTTOM_FRAC = 0.20
TOP_FRAC = 0.80

INDICATOR_COLS = ["grid_high", "grid_low", "grid_range", "grid_step",
                  "grid_mid", "grid_pos", "atr"]


def add_indicators(df: pd.DataFrame, n: int = GRID_N,
                   levels: int = LEVELS) -> pd.DataFrame:
    df = df.copy()
    gh = df["h"].rolling(n, min_periods=n).max()
    gl = df["l"].rolling(n, min_periods=n).min()
    grange = gh - gl
    df["grid_high"] = gh
    df["grid_low"] = gl
    df["grid_range"] = grange
    df["grid_step"] = grange / levels
    df["grid_mid"] = (gh + gl) / 2
    df["grid_pos"] = (df["c"] - gl) / grange.replace(0, np.nan)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
