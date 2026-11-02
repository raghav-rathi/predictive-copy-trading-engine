"""Hull Suite signals: the HMA's own turn.

    long_entry  -- HMA turns up (rising after falling/flat)
    short_entry -- HMA turns down (falling after rising/flat)
    long_exit   -- HMA turns down
    short_exit  -- HMA turns up
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hma = df["hma"].to_numpy()
    n = len(df)
    up = np.zeros(n, dtype=bool)
    up[1:] = hma[1:] > hma[:-1]
    long_e = np.zeros(n, dtype=bool)
    short_e = np.zeros(n, dtype=bool)
    long_e[1:] = up[1:] & ~up[:-1]
    short_e[1:] = ~up[1:] & up[:-1]
    df["long_entry"] = long_e
    df["short_entry"] = short_e
    df["long_exit"] = short_e
    df["short_exit"] = long_e
    return df
