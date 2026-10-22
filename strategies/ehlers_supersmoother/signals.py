"""SuperSmoother trend-cross signals, gated on the filter's slope.

Long when close crosses above the filter AND the filter is rising;
short when close crosses below the filter AND the filter is falling.
The slope gate keeps entries on the side of the developing trend -- a
cross against a falling filter is usually a pullback pop, not a turn.

    long_entry  = crossed_above(close, filt) & ss_rising
    short_entry = crossed_below(close, filt) & ss_falling

Exits are the opposite cross of close vs the filter, ungated: once a
position is open, a cross the other way means the leg failed.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    f = df["ss_filt"]
    cross_up = crossed_above(c, f).fillna(False)
    cross_dn = crossed_below(c, f).fillna(False)
    rising = df["ss_rising"].fillna(False)
    falling = df["ss_falling"].fillna(False)
    df["long_entry"] = (cross_up & rising).fillna(False).astype(bool)
    df["short_entry"] = (cross_dn & falling).fillna(False).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
