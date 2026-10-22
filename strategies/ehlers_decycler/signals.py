"""Decycler trend-cross signals.

The decycler line is the trend-only component of price. Trade the
crosses of close against it:

    long_entry  = crossed_above(close, decycler) & decycler rising
    short_entry = crossed_below(close, decycler) & decycler falling

The rising/falling confirmation (decycler > its own prior bar) means
the trend component itself is moving with the trade, not just price
noise poking through the line. Exits are the opposite cross: once
the trend component turns the other way, the reason for the position
is gone, so get out.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    d = df["decycler"]
    rising = (d > d.shift(1)).fillna(False)
    falling = (d < d.shift(1)).fillna(False)
    cross_up = crossed_above(c, d).fillna(False)
    cross_dn = crossed_below(c, d).fillna(False)
    df["long_entry"] = (cross_up & rising).fillna(False).astype(bool)
    df["short_entry"] = (cross_dn & falling).fillna(False).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
