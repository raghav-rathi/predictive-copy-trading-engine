"""Outside Bar signals: break of the prior outside bar's extreme."""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bull = df["outside_bull"].shift(1).fillna(False)
    bear = df["outside_bear"].shift(1).fillna(False)
    df["long_entry"] = (bull & (df["c"] > df["h"].shift(1))).astype(bool)
    df["short_entry"] = (bear & (df["c"] < df["l"].shift(1))).astype(bool)
    df["long_exit"] = df["outside_bear"].astype(bool)
    df["short_exit"] = df["outside_bull"].astype(bool)
    return df
