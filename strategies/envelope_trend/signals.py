"""Moving-average envelope breakout signals.

    long_entry  -- close crosses above the upper envelope band
    short_entry -- close crosses below the lower envelope band
    long_exit   -- close crosses back below the midline
    short_exit  -- close crosses back above the midline

NaN comparisons are False, so no signal fires before the envelope
exists. Boolean columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    up = df["env_upper"]
    lo = df["env_lower"]
    mid = df["env_mid"]
    long_entry = (c.shift(1) <= up.shift(1)) & (c > up)
    short_entry = (c.shift(1) >= lo.shift(1)) & (c < lo)
    long_exit = (c.shift(1) >= mid.shift(1)) & (c < mid)
    short_exit = (c.shift(1) <= mid.shift(1)) & (c > mid)
    df["long_entry"] = long_entry.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = short_entry.fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = long_exit.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = short_exit.fillna(False).to_numpy(dtype=bool)
    return df
