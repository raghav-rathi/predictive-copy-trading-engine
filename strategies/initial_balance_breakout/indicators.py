"""Initial Balance (Market Profile) indicators.

The Initial Balance (IB) is the high/low of the first 1h bar of each UTC
day (the 00:00-01:00 UTC bar, the first hour of the session on 24/7
crypto). The IB levels stay fixed for the whole UTC day. The 1x IB
extension targets are IB high + IB range (long target) and IB low -
IB range (short target).

All values are causal: a day's IB levels are set by that day's 00:00
UTC bar and only apply from that bar onward. If a UTC day has no
00:00 bar in the frame (e.g. a missing bar), the day's first available
bar is used as the IB bar instead (documented fallback).
"""

import numpy as np
import pandas as pd

INDICATOR_COLS = [
    "ib_high",
    "ib_low",
    "ib_range",
    "ib_target_long",
    "ib_target_short",
    "is_ib_bar",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    ib_high = np.full(n, np.nan)
    ib_low = np.full(n, np.nan)
    is_ib_bar = np.zeros(n, dtype=bool)
    if n:
        t = pd.to_datetime(df["t"], unit="ms", utc=True)
        hour = t.dt.hour.to_numpy()
        day = t.dt.floor("D").to_numpy()
        h = df["h"].to_numpy(dtype=float)
        l = df["l"].to_numpy(dtype=float)
        # Contiguous UTC-day segments.
        starts = np.flatnonzero(np.r_[True, day[1:] != day[:-1]])
        ends = np.r_[starts[1:], n]
        for s, e in zip(starts, ends):
            seg_hours = hour[s:e]
            if (seg_hours == 0).any():
                ib_pos = s + int(np.argmax(seg_hours == 0))
            else:
                ib_pos = s  # fallback: first bar of the day
            is_ib_bar[ib_pos] = True
            ib_high[ib_pos:e] = h[ib_pos]
            ib_low[ib_pos:e] = l[ib_pos]
    df["ib_high"] = ib_high
    df["ib_low"] = ib_low
    df["ib_range"] = ib_high - ib_low
    df["ib_target_long"] = ib_high + (ib_high - ib_low)
    df["ib_target_short"] = ib_low - (ib_high - ib_low)
    df["is_ib_bar"] = is_ib_bar
    return df
