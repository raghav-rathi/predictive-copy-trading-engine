"""McGinley Dynamic signals.

The Dynamic is used the way moving averages are used (McGinley himself
called it a smoothing mechanism, but the cross is the tradeable form):
  long_entry:  MD(10) crosses above MD(30)
  short_entry: MD(10) crosses below MD(30)
Exits: the opposite cross.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast, slow = df["md_fast"], df["md_slow"]
    df["long_entry"] = B.crossed_above(fast, slow).fillna(False)
    df["short_entry"] = B.crossed_below(fast, slow).fillna(False)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
