"""Supertrend signals.

Long  on flip to up (+1) with ADX > 20; exit on flip to down.
Short on flip to down (-1) with ADX > 20; exit on flip to up.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    flip_up = (df["st_dir"] == 1) & (df["st_dir_prev"] == -1)
    flip_dn = (df["st_dir"] == -1) & (df["st_dir_prev"] == 1)
    regime = df["adx"] > 20.0
    df["long_entry"] = flip_up & regime
    df["short_entry"] = flip_dn & regime
    df["long_exit"] = flip_dn
    df["short_exit"] = flip_up
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
