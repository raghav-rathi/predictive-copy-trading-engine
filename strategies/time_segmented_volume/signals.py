"""Time segmented volume signals.

Long: TSV(18) crosses above its zero line. Short: TSV(18) crosses
below its zero line. Exit a long on TSV crossing back below zero
(the opposite cross); exit a short on TSV crossing back above zero.
TSV on bar i uses only closes and volumes through bar i, so signals
on bar i use no future data.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tsv = df["tsv"]
    df["long_entry"] = crossed_above(tsv, 0).fillna(False).astype(bool)
    df["short_entry"] = crossed_below(tsv, 0).fillna(False).astype(bool)
    df["long_exit"] = crossed_below(tsv, 0).fillna(False).astype(bool)
    df["short_exit"] = crossed_above(tsv, 0).fillna(False).astype(bool)
    return df
