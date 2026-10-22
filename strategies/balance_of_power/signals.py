"""Balance of Power zero-cross signals.

Livshin's BOP is a control gauge: BOP above zero means buyers have
won the recent bars, below zero means sellers have. The zero line is
therefore the regime threshold, and a cross of the smoothed BOP
through zero marks a control shift:

    long_entry  = crossed_above(bop, 0)   (buyers take control)
    short_entry = crossed_below(bop, 0)   (sellers take control)

Exits are the opposite zero-cross: once buyers lose control, the long
thesis is gone, so get out — and vice versa for shorts.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import numpy as np
import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bop = df["bop"]
    zero = pd.Series(np.zeros(len(df)), index=df.index)
    cross_up = crossed_above(bop, zero).fillna(False)
    cross_dn = crossed_below(bop, zero).fillna(False)
    df["long_entry"] = cross_up.astype(bool)
    df["short_entry"] = cross_dn.astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
