"""Ehlers MAMA/FAMA cross signals.

Trend entries on the adaptive-average cross, confirmed by price being
on the MAMA side of the cross (filters the classic MAMA whipsaw where
the averages cross while price is still on the wrong side of MAMA).
Exits are the opposite cross -- the MAMA structure itself manages the
trade, so long_exit is the short-entry cross and short_exit is the
long-entry cross.

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    mama = df["mama"].ffill()
    fama = df["fama"].ffill()
    close = df["c"]

    cross_up = crossed_above(mama, fama).fillna(False)
    cross_dn = crossed_below(mama, fama).fillna(False)

    long_entry = (cross_up & (close > mama)).fillna(False)
    short_entry = (cross_dn & (close < mama)).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
