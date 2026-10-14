"""TRIX momentum signals.

long_entry  = TRIX crosses above its 9-bar signal line while below zero
              (momentum turning up from oversold)
short_entry = TRIX crosses below its 9-bar signal line while above zero
long_exit   = TRIX crosses back below its signal line
short_exit  = TRIX crosses back above its signal line
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    trix, sig = df["trix"], df["trix_signal"]
    long_x = B.crossed_above(trix, sig)
    short_x = B.crossed_below(trix, sig)
    df["long_entry"] = long_x & (trix < 0)
    df["short_entry"] = short_x & (trix > 0)
    df["long_exit"] = short_x
    df["short_exit"] = long_x
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
