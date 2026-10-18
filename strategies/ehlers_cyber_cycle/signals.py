"""Cyber Cycle signals (Ehlers).

Entries: long when the cycle crosses above its 1-bar-lagged trigger
(the cycle turning up), short when it crosses below (turning down).
Exits: the opposite cross — the strategy-defined exit is the same
turning-point logic reversed.  Risk-level exits (2xATR stop, 20-bar max
hold ~ half the dominant cycle) come from risk.py.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cyc = df["cyber_cycle"]
    trig = df["cyber_trigger"]
    cross_up = B.crossed_above(cyc, trig).fillna(False)
    cross_dn = B.crossed_below(cyc, trig).fillna(False)
    df["long_entry"] = cross_up
    df["short_entry"] = cross_dn
    df["long_exit"] = cross_dn
    df["short_exit"] = cross_up
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
