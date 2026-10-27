"""RSI trendline signals: enter on the break bar, exit on the
opposite break.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bull = df["rsi_break"] == 1
    bear = df["rsi_break"] == -1
    df["long_entry"] = bull.fillna(False).astype(bool)
    df["short_entry"] = bear.fillna(False).astype(bool)
    df["long_exit"] = bear.fillna(False).astype(bool)
    df["short_exit"] = bull.fillna(False).astype(bool)
    return df
