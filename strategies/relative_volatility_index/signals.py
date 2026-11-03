"""Relative Volatility Index signals.

Donald Dorsey Relative Volatility Index (10/10): volatility-weighted RSI — standard deviation of closes split into up/down buckets. Long on cross above 50, short on cross below 50; exits on the opposite cross.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["rvi"], 50).fillna(False)
    down = B.crossed_below(df["rvi"], 50).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
