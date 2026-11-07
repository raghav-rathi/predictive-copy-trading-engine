"""DEMA crossover signals (Mulloy, 1994).

Long when fast DEMA(12) crosses above slow DEMA(26); short on the
cross below. Exit on the reverse cross. All comparisons use only data
through bar i's close — no lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast = df["dema_fast"]
    slow = df["dema_slow"]
    long_entry = B.crossed_above(fast, slow)
    short_entry = B.crossed_below(fast, slow)
    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = df["short_entry"].copy()
    df["short_exit"] = df["long_entry"].copy()
    return df
