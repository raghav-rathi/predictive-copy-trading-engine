"""Murrey Math octave indicators.

Mechanism (Murrey Math Lines): take the trailing 64-bar high/low as the
"frame", split it into 8 equal octaves, and label the grid lines
L0=[0/8] ... L8=[8/8]; the 4/8 line (L4) is the pivot. Price tends to
reverse off the extreme lines (0/8, 8/8) and to stall/reject at the 4/8
pivot.

Frame choice (documented per spec): 64 bars is the classic Murrey Math
octave window and matches the referenced Murrey Math Lines v6 script's
default square-in-time frame. On 1h candles it spans ~2.7 days — short
enough to adapt to crypto's volatility regime shifts, long enough that
the octave grid is stable intraday. Sensitivity to this choice is
measured in CALIBRATION.md (32/64/128-bar frames).

No lookahead: every value on bar i uses bars through i only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

FRAME = 64        # trailing bars for the Murrey frame
ZONE_TOL = 0.10   # extreme-zone tolerance, in octave units


def add_indicators(
    df: pd.DataFrame,
    frame: int = FRAME,
    zone_tol: float = ZONE_TOL,
) -> pd.DataFrame:
    df = df.copy()
    hi = df["h"].rolling(frame, min_periods=frame).max()
    lo = df["l"].rolling(frame, min_periods=frame).min()
    octave = (hi - lo) / 8.0
    df["mm_hi"] = hi
    df["mm_lo"] = lo
    df["mm_octave"] = octave
    for k in range(9):
        df[f"mm_L{k}"] = lo + k * octave
    df["mm_mid"] = df["mm_L4"]  # 4/8 pivot
    # extreme-line touches (exact, per spec)
    df["mm_touch_0_8"] = df["l"] <= df["mm_L0"] + zone_tol * octave
    df["mm_touch_8_8"] = df["h"] >= df["mm_L8"] - zone_tol * octave
    # zones: bottom = 0/8..1/8 touched, top = 7/8..8/8 touched
    df["mm_touch_bottom"] = df["l"] <= df["mm_L1"] + zone_tol * octave
    df["mm_touch_top"] = df["h"] >= df["mm_L7"] - zone_tol * octave
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
