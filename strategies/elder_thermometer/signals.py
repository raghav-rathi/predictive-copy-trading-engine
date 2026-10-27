"""Thermometer signals: quiet range + trend-side location + a
close in the reversal direction. Exits on the mirror setup.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    quiet = df["therm"] < 0.6
    long = quiet & (df["c"] < df["sma20"]) & (df["c"] > df["o"])
    short = quiet & (df["c"] > df["sma20"]) & (df["c"] < df["o"])
    df["long_entry"] = long.fillna(False).astype(bool)
    df["short_entry"] = short.fillna(False).astype(bool)
    df["long_exit"] = short.fillna(False).astype(bool)
    df["short_exit"] = long.fillna(False).astype(bool)
    return df
