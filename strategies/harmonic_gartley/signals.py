"""Harmonic Gartley signals.

Enter on pattern completion: long on a bullish Gartley PRZ print,
short on a bearish one. Signal exits only on a fresh opposite pattern
(the harness's 4xATR target / 100-bar max hold do the trade management).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    gdir = df["gartley_dir"].fillna(0)
    bull = gdir == 1
    bear = gdir == -1
    df["long_entry"] = bull.fillna(False)
    df["short_entry"] = bear.fillna(False)
    df["long_exit"] = bear.fillna(False)
    df["short_exit"] = bull.fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
