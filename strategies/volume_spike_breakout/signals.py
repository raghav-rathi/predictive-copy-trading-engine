"""Breakout + volume spike signals."""

import numpy as np
import pandas as pd

VOL_MULT = 2.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    spike = df["v"] > VOL_MULT * df["vol_avg"]
    long_e = (df["c"] > df["vs_high"]) & spike
    short_e = (df["c"] < df["vs_low"]) & spike
    df["long_entry"] = long_e.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = short_e.fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = short_e.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = long_e.fillna(False).to_numpy(dtype=bool)
    return df
