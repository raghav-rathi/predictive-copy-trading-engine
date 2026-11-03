"""Pring Special K signals.

Martin Pring Special K: weighted sum of 10/15/20/30-bar ROCs (weights 1/2/3/4), smoothed with a 10-bar MA, traded against its own 10-bar signal line. Long on K cross above signal, short on cross below; exits on the opposite cross.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["special_k"], df["special_k_signal"]).fillna(False)
    down = B.crossed_below(df["special_k"], df["special_k_signal"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
