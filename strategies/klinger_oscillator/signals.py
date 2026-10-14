"""KVO signals (Klinger line vs its 13-EMA signal line).

long_entry  = KVO crosses above its signal line
short_entry = KVO crosses below its signal line
long_exit   = KVO crosses back below its signal line
short_exit  = KVO crosses back above its signal line
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    kvo, sig = df["kvo"], df["kvo_signal"]
    long_x = B.crossed_above(kvo, sig)
    short_x = B.crossed_below(kvo, sig)
    df["long_entry"] = long_x
    df["short_entry"] = short_x
    df["long_exit"] = short_x
    df["short_exit"] = long_x
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
