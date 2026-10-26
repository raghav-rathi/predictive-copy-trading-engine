"""Tweezer top short, tweezer bottom long, opposite exits."""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h, l, c = df["h"], df["l"], df["c"]
    top = ((h - h.shift(1)).abs() <= 0.0015 * h) & (c < c.shift(1))
    bottom = ((l - l.shift(1)).abs() <= 0.0015 * l) & (c > c.shift(1))
    df["long_entry"] = bottom.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = top.fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = top.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = bottom.fillna(False).to_numpy(dtype=bool)
    return df
