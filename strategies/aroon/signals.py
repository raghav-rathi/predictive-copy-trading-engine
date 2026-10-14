"""Aroon signals (Chande's fresh-trend cross).

long_entry  = AroonUp >= 70 and crosses above AroonDown
short_entry = AroonDown >= 70 and crosses above AroonUp
long_exit   = AroonUp crosses below AroonDown
short_exit  = AroonDown crosses below AroonUp
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B
from strategies.aroon import indicators as ind


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up, dn = df["aroon_up"], df["aroon_down"]
    long_x = B.crossed_above(up, dn)
    short_x = B.crossed_above(dn, up)
    df["long_entry"] = (up >= ind.STRONG) & long_x
    df["short_entry"] = (dn >= ind.STRONG) & short_x
    df["long_exit"] = B.crossed_below(up, dn)
    df["short_exit"] = B.crossed_below(dn, up)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
