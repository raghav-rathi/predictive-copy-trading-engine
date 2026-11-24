"""SuperSmoother trend crossover signals.

Long when the fast SuperSmoother(10) crosses above the slow
SuperSmoother(30); short when it crosses below. Exit on the
opposite cross — the crossover is both the entry and the
premise-expiry signal, so a position is held only while the fast
line stays on its side of the slow line.

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast = df["ss_fast"]
    slow = df["ss_slow"]

    cross_up = crossed_above(fast, slow).fillna(False)
    cross_down = crossed_below(fast, slow).fillna(False)

    df["long_entry"] = cross_up.astype(bool)
    df["short_entry"] = cross_down.astype(bool)
    df["long_exit"] = cross_down.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
