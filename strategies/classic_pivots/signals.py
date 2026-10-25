"""Classic pivot breakout signals.

    long_entry  -- close crosses above R1
    short_entry -- close crosses below S1
    long_exit   -- close crosses back below PP
    short_exit  -- close crosses back above PP

NaN comparisons are False, so no signal fires on the first bar.
Boolean columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    pp = df["piv_pp"]
    r1 = df["piv_r1"]
    s1 = df["piv_s1"]
    long_entry = (c.shift(1) <= r1.shift(1)) & (c > r1)
    short_entry = (c.shift(1) >= s1.shift(1)) & (c < s1)
    long_exit = (c.shift(1) >= pp.shift(1)) & (c < pp)
    short_exit = (c.shift(1) <= pp.shift(1)) & (c > pp)
    df["long_entry"] = long_entry.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = short_entry.fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = long_exit.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = short_exit.fillna(False).to_numpy(dtype=bool)
    return df
