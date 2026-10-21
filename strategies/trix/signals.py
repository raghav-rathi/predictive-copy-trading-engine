"""TRIX turn-up-from-negative / turn-down-from-positive signals.

Classic TRIX trading rule (Hutson): buy when the TRIX line crosses
above its signal line *while still below zero* — momentum turns up
from washed-out territory, not from an already-overbought read. Short
when TRIX crosses below its signal while still above zero.

    long_entry  = crossed_above(trix, trix_signal) & (trix < 0)
    short_entry = crossed_below(trix, trix_signal) & (trix > 0)

Exits are the opposite cross regardless of territory: once a position
is open, a cross the other way means the momentum turn failed, so get
out even if TRIX never reached zero.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tx = df["trix"]
    sg = df["trix_signal"]
    cross_up = crossed_above(tx, sg).fillna(False)
    cross_dn = crossed_below(tx, sg).fillna(False)
    df["long_entry"] = (cross_up & (tx < 0)).fillna(False).astype(bool)
    df["short_entry"] = (cross_dn & (tx > 0)).fillna(False).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
