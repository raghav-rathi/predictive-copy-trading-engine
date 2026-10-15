"""ZLEMA signals — the de-lagged pair traded as a moving-average
crossover:
  long_entry:  ZLEMA(10) crosses above ZLEMA(30)
  short_entry: ZLEMA(10) crosses below ZLEMA(30)
Exits: the opposite cross.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast, slow = df["zlema_fast"], df["zlema_slow"]
    df["long_entry"] = B.crossed_above(fast, slow).fillna(False)
    df["short_entry"] = B.crossed_below(fast, slow).fillna(False)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
