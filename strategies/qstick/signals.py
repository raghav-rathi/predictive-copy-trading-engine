"""Qstick signals (zero-line cross system).

long_entry  = Qstick crosses above zero (buying pressure takes over)
short_entry = Qstick crosses below zero (selling pressure takes over)
long_exit   = Qstick crosses back below zero
short_exit  = Qstick crosses back above zero
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    q = df["qstick"]
    long_x = B.crossed_above(q, 0.0)
    short_x = B.crossed_below(q, 0.0)
    df["long_entry"] = long_x
    df["short_entry"] = short_x
    df["long_exit"] = short_x
    df["short_exit"] = long_x
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
