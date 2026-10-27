"""Bat signals: long on a bullish Bat PRZ print, short on a
bearish one; exit on the opposite pattern.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bull = df["bat_dir"] == 1
    bear = df["bat_dir"] == -1
    df["long_entry"] = bull.fillna(False)
    df["short_entry"] = bear.fillna(False)
    df["long_exit"] = bear.fillna(False)
    df["short_exit"] = bull.fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
