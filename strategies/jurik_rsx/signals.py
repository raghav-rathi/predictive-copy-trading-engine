"""Jurik RSX signals.

    long_entry  -- RSX crosses above 50 with RSX rising
                   (RSX > previous RSX)
    short_entry -- RSX crosses below 50 with RSX falling
    long_exit   -- RSX crosses back below 50, or RSX hits 80
    short_exit  -- RSX crosses back above 50, or RSX hits 20

Skip rule: no entry if RSX is flat — |ΔRSX| < 0.5 for 3 consecutive
bars — because a flat RSX crossing 50 is noise, not momentum.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

FLAT_DELTA = 0.5  # shipped default: |ΔRSX| below this counts as flat
FLAT_BARS = 3


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsx = df["rsx"]
    prev = rsx.shift(1)
    d = rsx.diff().abs()
    flat = (
        (d < FLAT_DELTA)
        & (d.shift(1) < FLAT_DELTA)
        & (d.shift(2) < FLAT_DELTA)
    ).fillna(False)
    cross_up = crossed_above(rsx, 50).fillna(False)
    cross_dn = crossed_below(rsx, 50).fillna(False)
    df["long_entry"] = (
        cross_up & (rsx > prev).fillna(False) & (~flat)
    ).astype(bool)
    df["short_entry"] = (
        cross_dn & (rsx < prev).fillna(False) & (~flat)
    ).astype(bool)
    df["long_exit"] = (cross_dn | (rsx >= 80)).fillna(False).astype(bool)
    df["short_exit"] = (cross_up | (rsx <= 20)).fillna(False).astype(bool)
    return df
