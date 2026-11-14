"""Laguerre filter crossover signals.

    long_entry  = crossed_above(close, laguerre) & laguerre rising
    short_entry = crossed_below(close, laguerre) & laguerre falling

The slope condition keeps entries out of flat-filter chop: a cross
only counts when the filter itself is already moving in the trade's
direction. Exits are the opposite price/filter cross regardless of
slope — once a position is open, price crossing back through the
filter means the leg failed.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    filt = df["laguerre"]
    rising = (filt > filt.shift(1)).fillna(False)
    falling = (filt < filt.shift(1)).fillna(False)
    cross_up = crossed_above(c, filt).fillna(False)
    cross_dn = crossed_below(c, filt).fillna(False)
    df["long_entry"] = (cross_up & rising).astype(bool)
    df["short_entry"] = (cross_dn & falling).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
