"""Gap and Go signals: break of the gap bar's extreme within 3 bars."""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    gap_high = df["gap_high"]
    gap_low = df["gap_low"]
    # Entry bars are strictly after the gap bar itself: the level at the
    # prior bar must already exist, so a gap bar cannot trigger on itself.
    prev_high = gap_high.shift(1)
    prev_low = gap_low.shift(1)
    prev_mid = df["gap_mid"].shift(1)
    df["long_entry"] = (df["c"] > prev_high).fillna(False).astype(bool)
    df["short_entry"] = (df["c"] < prev_low).fillna(False).astype(bool)
    df["long_exit"] = (df["c"] < prev_mid).fillna(False).astype(bool)
    df["short_exit"] = (df["c"] > prev_mid).fillna(False).astype(bool)
    return df
