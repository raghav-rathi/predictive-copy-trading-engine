"""ZLEMA signals: fast/slow Zero Lag EMA cross."""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = B.crossed_above(df["zlema20"], df["zlema50"]).astype(bool)
    df["short_entry"] = B.crossed_below(df["zlema20"], df["zlema50"]).astype(bool)
    df["long_exit"] = B.crossed_below(df["zlema20"], df["zlema50"]).astype(bool)
    df["short_exit"] = B.crossed_above(df["zlema20"], df["zlema50"]).astype(bool)
    return df
