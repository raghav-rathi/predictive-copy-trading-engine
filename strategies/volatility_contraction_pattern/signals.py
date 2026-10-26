"""VCP long entry: breakout of a contracting, uptrending base on volume."""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    uptrend = (df["c"] > df["sma50"]) & (df["sma50"] > df["sma50"].shift(5))
    contracting = (df["atr_ratio"].shift(1) < 1.0) & (df["range_pct"] < 0.02)
    breakout = (df["c"] > df["vcp_high"]) & (df["v"] > df["vol_avg"])
    long_e = uptrend & contracting & breakout
    exit_e = df["c"] < df["sma50"]
    df["long_entry"] = long_e.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = np.zeros(len(df), dtype=bool)
    df["long_exit"] = exit_e.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = np.zeros(len(df), dtype=bool)
    return df
