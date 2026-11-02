"""Gann HiLo Activator signals.

    long_entry  -- activator state flips to bullish (+1)
    short_entry -- activator state flips to bearish (-1)
    long_exit   -- activator state flips to bearish
    short_exit  -- activator state flips to bullish
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    state = df["hilo_state"].to_numpy()
    n = len(df)
    long_e = np.zeros(n, dtype=bool)
    short_e = np.zeros(n, dtype=bool)
    long_e[1:] = (state[1:] == 1) & (state[:-1] == -1)
    short_e[1:] = (state[1:] == -1) & (state[:-1] == 1)
    df["long_entry"] = long_e
    df["short_entry"] = short_e
    df["long_exit"] = short_e
    df["short_exit"] = long_e
    return df
