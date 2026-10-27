"""Hammer signals: long on a hammer close, short on a shooting
star close; exit on the opposite pattern.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bull = df["pattern"] == 1
    bear = df["pattern"] == -1
    df["long_entry"] = bull.fillna(False).astype(bool)
    df["short_entry"] = bear.fillna(False).astype(bool)
    df["long_exit"] = bear.fillna(False).astype(bool)
    df["short_exit"] = bull.fillna(False).astype(bool)
    return df
