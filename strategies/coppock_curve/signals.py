"""Coppock Curve zero-cross signals.

Entries: the Coppock line crossing the zero line is the classic
Coppock "buy" trigger (momentum turning from negative to positive),
mirrored for shorts:
    long_entry  = crossed_above(coppock, 0)
    short_entry = crossed_below(coppock, 0)
Exits are the opposite cross (a cross back through zero reverses the
momentum read). Signal columns are boolean, no NaN, no lookahead
(execution at next-bar open is handled by the harness).
"""

import numpy as np
import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cop = df["coppock"]
    zero = pd.Series(np.zeros(len(df)), index=df.index)
    cross_up = crossed_above(cop, zero).fillna(False)
    cross_dn = crossed_below(cop, zero).fillna(False)
    df["long_entry"] = cross_up.astype(bool)
    df["short_entry"] = cross_dn.astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
