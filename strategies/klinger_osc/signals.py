"""Klinger Volume Oscillator signals.

Long entry: kvo crosses above the signal line (volume force confirmed
the upside through a high-volume trend bar).
Short entry: kvo crosses below the signal line.
Exits: the opposite cross (pure cross-based, no extra filter).

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = crossed_above(df["kvo"], df["ksig"]).fillna(False)
    cross_dn = crossed_below(df["kvo"], df["ksig"]).fillna(False)

    df["long_entry"] = cross_up.astype(bool)
    df["short_entry"] = cross_dn.astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
