"""Parabolic SAR stop-and-reverse signals.

Entry: long_entry fires when sar_dir flips -1 -> +1 (SAR drops below
price); short_entry fires when it flips +1 -> -1 (SAR rises above price).
Exits are the mirror flips: long_exit == short_entry and
short_exit == long_entry, because the SAR is the trailing stop --
a reversal that takes out the old stop simultaneously opens the new
position. No lookahead: flips are computed on bar i from data through i
and execute at bar i+1's open.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev = df["sar_dir"].shift(1)
    long_entry = (df["sar_dir"] == 1) & (prev == -1)
    short_entry = (df["sar_dir"] == -1) & (prev == 1)
    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = df["short_entry"].copy()
    df["short_exit"] = df["long_entry"].copy()
    return df
