"""SWMA fast/slow crossover signals.

    long_entry  = crossed_above(swma_fast, swma_slow)
    short_entry = crossed_below(swma_fast, swma_slow)

Exits are the opposite cross: once a position is open, a cross the
other way means the trend leg failed, so get out.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast = df["swma_fast"]
    slow = df["swma_slow"]
    cross_up = crossed_above(fast, slow).fillna(False)
    cross_dn = crossed_below(fast, slow).fillna(False)
    df["long_entry"] = cross_up.astype(bool)
    df["short_entry"] = cross_dn.astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
