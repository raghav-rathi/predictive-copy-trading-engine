"""Kairi Relative Index signals.

Kairi Relative Index (25): (close - SMA25) / SMA25 x 100. Mean reversion: long on recovery cross above -5 after an oversold dip, short on breakdown cross below +5 after an overbought peak; exits at the mean (0).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_e = B.crossed_above(df["kairi"], -5).fillna(False)
    short_e = B.crossed_below(df["kairi"], 5).fillna(False)
    df["long_entry"] = long_e.astype(bool)
    df["short_entry"] = short_e.astype(bool)
    df["long_exit"] = B.crossed_above(df["kairi"], 0).fillna(False).astype(bool)
    df["short_exit"] = B.crossed_below(df["kairi"], 0).fillna(False).astype(bool)
    return df
