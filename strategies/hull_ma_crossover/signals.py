"""Hull MA crossover signals.

Long on HMA(16) crossing above HMA(32) with the fast HMA slope positive;
short on a cross below with the slope negative. Exit on the opposite
cross. Signals use only data through bar i's close.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast = df["hma_fast"]
    slow = df["hma_slow"]
    slope_up = (fast > fast.shift(1)).fillna(False)
    slope_down = (fast < fast.shift(1)).fillna(False)
    df["long_entry"] = (B.crossed_above(fast, slow) & slope_up).astype(bool)
    df["short_entry"] = (B.crossed_below(fast, slow) & slope_down).astype(bool)
    df["long_exit"] = B.crossed_below(fast, slow).astype(bool)
    df["short_exit"] = B.crossed_above(fast, slow).astype(bool)
    return df
