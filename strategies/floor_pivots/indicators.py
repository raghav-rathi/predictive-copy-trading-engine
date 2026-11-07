"""Floor-trader pivot indicators.

Classic floor-trader pivots, recomputed every bar from the trailing 24
completed 1h bars (one "session" on 1h crypto data): with H = max high,
L = min low and C = close of the last completed bar in the window,

    PP = (H + L + C) / 3
    R1 = 2*PP - L      S1 = 2*PP - H
    R2 = PP + (H - L)  S2 = PP - (H - L)

The window uses only bars i-24..i-1 for the levels evaluated on bar i,
so no lookahead. Volume filter uses the 20-bar average volume over the
trailing 20 completed bars.
"""

import numpy as np
import pandas as pd

SESSION_BARS = 24
VOL_AVG_BARS = 20

INDICATOR_COLS = [
    "fp_pp",
    "fp_r1",
    "fp_s1",
    "fp_r2",
    "fp_s2",
    "fp_vol_avg",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].shift(1)
    l = df["l"].shift(1)
    c_prev = df["c"].shift(1)
    h24 = h.rolling(SESSION_BARS, min_periods=SESSION_BARS).max()
    l24 = l.rolling(SESSION_BARS, min_periods=SESSION_BARS).min()
    pp = (h24 + l24 + c_prev) / 3.0
    df["fp_pp"] = pp
    df["fp_r1"] = 2.0 * pp - l24
    df["fp_s1"] = 2.0 * pp - h24
    df["fp_r2"] = pp + (h24 - l24)
    df["fp_s2"] = pp - (h24 - l24)
    df["fp_vol_avg"] = df["v"].shift(1).rolling(VOL_AVG_BARS, min_periods=VOL_AVG_BARS).mean()
    return df
