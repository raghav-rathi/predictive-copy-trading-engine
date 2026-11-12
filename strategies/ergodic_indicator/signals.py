"""Ergodic oscillator signals (Blau's canonical signal-line cross).

Long entry:  ergodic crosses above its signal line.
Short entry: ergodic crosses below its signal line.
Long exit:   ergodic crosses below its signal line (opposite cross).
Short exit:  ergodic crosses above its signal line.

This is the raw signal-line cross with no extra filter -- unlike the
repo's true_strength_index strategy, which adds a zero-territory
filter to entries (see CALIBRATION.md).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies, so
in practice most positions end on the stop/trail/max-hold before the
opposite cross; the opposite cross is the system-defined exit.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = crossed_above(df["ergodic"], df["ergodic_signal"]).fillna(False)
    cross_dn = crossed_below(df["ergodic"], df["ergodic_signal"]).fillna(False)
    df["long_entry"] = cross_up.astype(bool)
    df["short_entry"] = cross_dn.astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
