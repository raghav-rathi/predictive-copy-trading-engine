"""Ehlers universal oscillator signals.

Long on the AGC-normalized band-pass output crossing above
its trigger line (0.9x the prior bar's normalized output),
short on it crossing below; exit on the opposite cross (so
long_exit is the short-entry cross and vice versa).

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bp_norm = df["bp_norm"]
    trigger = df["trigger"]
    up = crossed_above(bp_norm, trigger)
    down = crossed_below(bp_norm, trigger)
    df["long_entry"] = up.fillna(False).astype(bool)
    df["short_entry"] = down.fillna(False).astype(bool)
    df["long_exit"] = down.fillna(False).astype(bool)
    df["short_exit"] = up.fillna(False).astype(bool)
    return df
