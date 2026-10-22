"""DEMA fast/slow cross signals.

Long when the fast DEMA crosses above the slow DEMA — the
lag-reduced trend line has turned up relative to the slow anchor.
Short on the cross below. Exits are the opposite cross: once the
fast line rolls back through the slow one the trend read is
invalidated, so the position is closed.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast = df["dema_fast"]
    slow = df["dema_slow"]
    cross_up = crossed_above(fast, slow).fillna(False)
    cross_dn = crossed_below(fast, slow).fillna(False)
    df["long_entry"] = cross_up.astype(bool)
    df["short_entry"] = cross_dn.astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
