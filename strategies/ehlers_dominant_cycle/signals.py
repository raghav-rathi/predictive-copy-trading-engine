"""Ehlers dominant-cycle signals.

Long on the band-pass output crossing above zero, short on
it crossing below zero; exit on the opposite cross (so
long_exit is the short-entry cross and vice versa). The
dominant-cycle column is diagnostic only — it is not used to
gate or size trades.

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bp = df["bp"]
    up = crossed_above(bp, 0.0)
    down = crossed_below(bp, 0.0)
    df["long_entry"] = up.fillna(False).astype(bool)
    df["short_entry"] = down.fillna(False).astype(bool)
    df["long_exit"] = down.fillna(False).astype(bool)
    df["short_exit"] = up.fillna(False).astype(bool)
    return df
