"""Narrow-range breakout (NR7) signals.

Entry: on a bar within 24 bars after an NR7 setup bar, close above
the setup bar's high -> long (only when the trend at the setup bar
was up, SMA50 > SMA200); close below the setup bar's low -> short
(only when the trend at the setup bar was down). Only the most recent
setup bar governs.
Exit: long_exit when the close falls back below the setup bar's low,
or when a new short-trend NR7 setup bar triggers; short_exit mirror.
All setup levels come from bars strictly before bar i, so signals on
bar i use only data through bar i's close.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    setup_high = df["nr_setup_high"]
    setup_low = df["nr_setup_low"]
    setup_dir = df["nr_setup_dir"]
    is_nr7 = df["nr_is_nr7"].fillna(False)
    sma50 = df["sma50"]
    sma200 = df["sma200"]
    long_setup = is_nr7 & (sma50 > sma200)
    short_setup = is_nr7 & (sma50 < sma200)
    df["long_entry"] = ((c > setup_high) & (setup_dir == 1.0)).fillna(False).astype(bool)
    df["short_entry"] = ((c < setup_low) & (setup_dir == -1.0)).fillna(False).astype(bool)
    df["long_exit"] = ((c < setup_low) | short_setup).fillna(False).astype(bool)
    df["short_exit"] = ((c > setup_high) | long_setup).fillna(False).astype(bool)
    return df
