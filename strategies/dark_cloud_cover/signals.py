"""Dark cloud cover / piercing pattern signals.

Short: dark cloud cover completes on bar i -> enter on bar 2's close.
Exit the short on a close above bar 2's high. Long: piercing pattern
completes on bar i -> enter; exit on a close below bar 2's low. Bar
2's extremes are forward-filled from the pattern bar and checked from
the following bar on (shifted by 1), so the exit cannot trigger on
the pattern bar itself. Signals on bar i use only data through bar
i's close.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    df["long_entry"] = df["dcc_bullish"].astype(bool)
    df["short_entry"] = df["dcc_bearish"].astype(bool)
    bar2_high = df["dcc_bar2_high"].ffill().shift(1)
    bar2_low = df["dcc_bar2_low"].ffill().shift(1)
    df["long_exit"] = (c < bar2_low).fillna(False).astype(bool)
    df["short_exit"] = (c > bar2_high).fillna(False).astype(bool)
    return df
