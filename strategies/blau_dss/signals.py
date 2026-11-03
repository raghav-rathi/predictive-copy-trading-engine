"""Blau Double Smoothed Stochastic signals.

William Blau Double Smoothed Stochastic (21, 3, 3): stochastic %K double-smoothed with EMAs and traded against its 3-bar EMA trigger. Long on DSS cross above trigger, short on cross below; exits on the opposite cross.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["dss"], df["dss_trigger"]).fillna(False)
    down = B.crossed_below(df["dss"], df["dss_trigger"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
