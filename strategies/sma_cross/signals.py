"""SMA crossover signals.

    long_entry  -- fast SMA crosses above slow SMA
    short_entry -- fast SMA crosses below slow SMA
    long_exit   -- fast SMA crosses below slow SMA (the opposite cross)
    short_exit  -- fast SMA crosses above slow SMA

NaN comparisons are False, so no signal fires before both SMAs exist.
Signals are boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    f = df["sma_fast"]
    s = df["sma_slow"]
    cross_up = (f.shift(1) <= s.shift(1)) & (f > s)
    cross_down = (f.shift(1) >= s.shift(1)) & (f < s)
    df["long_entry"] = cross_up.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = cross_down.fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = cross_down.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = cross_up.fillna(False).to_numpy(dtype=bool)
    return df
