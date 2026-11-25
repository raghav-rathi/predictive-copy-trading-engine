"""Coppock Curve signals.

Canonical Coppock buy: the curve turns up while below zero (the
below-zero hook — the signal Coppock himself traded). Short is the
mirror extension (turns down while above zero), documented as a
non-canonical extension: Coppock's original is long-only. Exit on
the opposite turn, or on the curve crossing zero against the
position.

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cp = df["coppock"]
    df["long_entry"] = (
        df["turn_up"] & (cp < 0)
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        df["turn_down"] & (cp > 0)
    ).fillna(False).astype(bool)
    df["long_exit"] = (
        df["turn_down"] | crossed_above(cp, 0)
    ).fillna(False).astype(bool)
    df["short_exit"] = (
        df["turn_up"] | crossed_below(cp, 0)
    ).fillna(False).astype(bool)
    return df
