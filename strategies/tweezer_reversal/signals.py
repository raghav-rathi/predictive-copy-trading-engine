"""Tweezer top/bottom reversal signals.

Long: tweezer bottom completes on bar i -> enter at bar i's close.
Exit the long on a close below the tweezer low (min of the two
lows, forward-filled from the pattern bar). Short: tweezer top
completes -> enter; exit on a close above the tweezer high.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    df["long_entry"] = df["twz_bottom"].fillna(False).astype(bool)
    df["short_entry"] = df["twz_top"].fillna(False).astype(bool)
    df["long_exit"] = (c < df["twz_low"]).fillna(False).astype(bool)
    df["short_exit"] = (c > df["twz_high"]).fillna(False).astype(bool)
    return df
