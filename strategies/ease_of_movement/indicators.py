"""Ease of Movement indicators (Richard Arms).

1-bar EMV = distance_moved / box_ratio, where
  distance_moved = midpoint - prev_midpoint,  midpoint = (H + L) / 2
  box_ratio     = volume / (H - L)

A large price move on small volume moves "easily" (high EMV); the same
move on huge volume barely moves (low EMV). The traded line is the
14-bar SMA of the 1-bar values. Degenerate bars (H == L) contribute 0.
No lookahead: every value on bar i uses bars through i only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

EMV_SMOOTH = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h, l, v = df["h"], df["l"], df["v"]
    mid = (h + l) / 2.0
    dist = mid.diff()
    box = v / (h - l).replace(0.0, np.nan)
    emv1 = (dist / box.replace(0.0, np.nan)).fillna(0.0)
    df["emv"] = B.sma(emv1, EMV_SMOOTH)
    df["emv_raw"] = emv1
    return df
