"""TEMA(9) vs TEMA(21) cross signals.

Long entry:  TEMA(9) crosses above TEMA(21).
Short entry: TEMA(9) crosses below TEMA(21).
Long exit:   TEMA(9) crosses back below TEMA(21) (the opposite cross).
Short exit:  TEMA(9) crosses back above TEMA(21).

No regime filter: unlike tema_trend (TEMA 20/50 + SMA200 filter),
this system trades every cross. The strategy is always aligned with
whichever TEMA is on top, subject to the risk layer's stop/trail.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast = df["tema_fast"]
    slow = df["tema_slow"]
    cross_up = crossed_above(fast, slow).fillna(False)
    cross_dn = crossed_below(fast, slow).fillna(False)
    df["long_entry"] = cross_up.astype(bool)
    df["short_entry"] = cross_dn.astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
