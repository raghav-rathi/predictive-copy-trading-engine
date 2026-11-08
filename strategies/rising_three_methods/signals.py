"""Rising/falling three methods signals.

Long: rising three methods completes on bar 5 -> enter at bar 5's
close. Exit the long on a close below bar 1's low (forward-filled
from the pattern bar). Short: falling three methods completes ->
enter; exit on a close above bar 1's high.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    df["long_entry"] = df["rtm_bullish"].fillna(False).astype(bool)
    df["short_entry"] = df["rtm_bearish"].fillna(False).astype(bool)
    df["long_exit"] = (c < df["rtm_bar1_low"]).fillna(False).astype(bool)
    df["short_exit"] = (c > df["rtm_bar1_high"]).fillna(False).astype(bool)
    return df
