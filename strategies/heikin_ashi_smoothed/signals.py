"""Smoothed Heikin-Ashi signals.

Long entry: smoothed HA close crosses above smoothed HA open
(the smoothed candle turns bullish). Short entry: cross below.
Exits are the opposite cross — the position lives exactly as long
as the smoothed HA trend agrees with it. Boolean columns, no NaN,
no lookahead (crosses read bars <= i; the harness executes at
bar i+1's open).
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sc = df["ha_close_smooth"]
    so = df["ha_open_smooth"]

    up = B.crossed_above(sc, so).fillna(False)
    dn = B.crossed_below(sc, so).fillna(False)

    df["long_entry"] = np.asarray(up, dtype=bool)
    df["short_entry"] = np.asarray(dn, dtype=bool)
    df["long_exit"] = np.asarray(dn, dtype=bool)
    df["short_exit"] = np.asarray(up, dtype=bool)
    return df
