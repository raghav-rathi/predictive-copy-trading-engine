"""Marubozu signals: enter on the conviction close, exit on the
opposite marubozu.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bull = df["marubozu_dir"] == 1
    bear = df["marubozu_dir"] == -1
    df["long_entry"] = bull.fillna(False).astype(bool)
    df["short_entry"] = bear.fillna(False).astype(bool)
    df["long_exit"] = bear.fillna(False).astype(bool)
    df["short_exit"] = bull.fillna(False).astype(bool)
    return df
