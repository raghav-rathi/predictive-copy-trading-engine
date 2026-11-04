"""Acceleration Bands signals: two closes outside, exit on close back inside."""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    above = df["c"] > df["ab_upper"]
    below = df["c"] < df["ab_lower"]
    df["long_entry"] = (above & above.shift(1).fillna(False)).astype(bool)
    df["short_entry"] = (below & below.shift(1).fillna(False)).astype(bool)
    df["long_exit"] = (df["c"] < df["ab_upper"]).astype(bool)
    df["short_exit"] = (df["c"] > df["ab_lower"]).astype(bool)
    return df
