"""ADX trend system signals (Wilder, 1978).

Long when +DI crosses above -DI and ADX > 25; short when -DI crosses
above +DI and ADX > 25. Exit on the opposite DI cross or ADX falling
below 20.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = (
        B.crossed_above(df["plus_di"], df["minus_di"]) & (df["adx"] > 25)
    ).astype(bool)
    df["short_entry"] = (
        B.crossed_below(df["plus_di"], df["minus_di"]) & (df["adx"] > 25)
    ).astype(bool)
    df["long_exit"] = (
        B.crossed_below(df["plus_di"], df["minus_di"]) | (df["adx"] < 20)
    ).astype(bool)
    df["short_exit"] = (
        B.crossed_above(df["plus_di"], df["minus_di"]) | (df["adx"] < 20)
    ).astype(bool)
    return df
