"""Gated flips: Supertrend flip + ADX>25 enters; opposite flip exits."""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = df["st_dir"]
    flip_up = (d == 1) & (d.shift(1) == -1)
    flip_down = (d == -1) & (d.shift(1) == 1)
    strong = df["adx"] > 25
    df["long_entry"] = (flip_up & strong).fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = (flip_down & strong).fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = flip_down.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = flip_up.fillna(False).to_numpy(dtype=bool)
    return df
