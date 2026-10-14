"""Coppock Curve signals (zero-line cross system).

long_entry  = Coppock crosses above 0 (momentum regime turns positive)
short_entry = Coppock crosses below 0 (momentum regime turns negative)
long_exit   = Coppock crosses back below 0
short_exit  = Coppock crosses back above 0
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cc = df["coppock"]
    long_x = B.crossed_above(cc, 0.0)
    short_x = B.crossed_below(cc, 0.0)
    df["long_entry"] = long_x
    df["short_entry"] = short_x
    df["long_exit"] = short_x
    df["short_exit"] = long_x
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
