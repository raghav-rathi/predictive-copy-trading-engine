"""Kagi yang/yin transition signals.

Long on the thin -> thick (yin -> yang) transition -- a rising column
has grown a shoulder above the previous column's high. Short on the
thick -> thin transition -- a falling column has made a waist below the
previous column's low. Exits on the opposite transition: the kagi
structure itself manages the trade, so long_exit is the short-entry
transition and short_exit is the long-entry transition.

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    thick = df["kagi_thick"].fillna(False).astype(bool)
    prev = thick.shift(1).fillna(False).astype(bool)
    long_entry = (thick & ~prev).fillna(False)
    short_entry = (~thick & prev).fillna(False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = short_entry.astype(bool)
    df["short_exit"] = long_entry.astype(bool)
    return df
