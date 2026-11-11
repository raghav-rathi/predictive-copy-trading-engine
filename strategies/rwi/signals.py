"""Random Walk Index signals (Chande & Kroll).

Long entry: RWI-high crosses above 1.0 (up-move beats the random-walk
yardstick — a real trend is under way).
Short entry: RWI-low crosses above 1.0.
Long exit: RWI-low crosses above 1.0 (the opposite RWI takes over).
Short exit: RWI-high crosses above 1.0.

All inputs are computed from data through bar i's close, so signals
on bar i use no future data. The harness executes at bar i+1's open.
"""

import pandas as pd

from strategies.base import crossed_above

LEVEL = 1.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry = crossed_above(df["rwi_high"], LEVEL)
    short_entry = crossed_above(df["rwi_low"], LEVEL)
    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    # Exits are the opposite RWI crossing above 1.0 (a reversal signal).
    df["long_exit"] = short_entry.fillna(False).astype(bool)
    df["short_exit"] = long_entry.fillna(False).astype(bool)
    return df
