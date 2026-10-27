"""Doji signals: enter on the extreme doji, exit on the opposite
doji.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bull = df["doji_dir"] == 1
    bear = df["doji_dir"] == -1
    df["long_entry"] = bull.fillna(False).astype(bool)
    df["short_entry"] = bear.fillna(False).astype(bool)
    df["long_exit"] = bear.fillna(False).astype(bool)
    df["short_exit"] = bull.fillna(False).astype(bool)
    return df
