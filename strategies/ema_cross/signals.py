"""EMA crossover signals.

    long_entry  -- fast EMA crosses above slow EMA
    short_entry -- fast EMA crosses below slow EMA
    long_exit   -- fast EMA crosses below slow EMA (the opposite cross)
    short_exit  -- fast EMA crosses above slow EMA

NaN comparisons are False, so no signal fires before both EMAs exist.
Signals are boolean, no NaN, no lookahead: a cross on bar i uses only
closes through bar i, and the harness executes at bar i+1's open.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    f = df["ema_fast"]
    s = df["ema_slow"]
    cross_up = (f.shift(1) <= s.shift(1)) & (f > s)
    cross_down = (f.shift(1) >= s.shift(1)) & (f < s)
    df["long_entry"] = cross_up.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = cross_down.fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = cross_down.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = cross_up.fillna(False).to_numpy(dtype=bool)
    return df
