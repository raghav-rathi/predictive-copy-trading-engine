"""KST signals (Pring's signal-line cross).

long_entry  = KST crosses above its 9-bar signal line
short_entry = KST crosses below its 9-bar signal line
long_exit   = KST crosses back below its signal line
short_exit  = KST crosses back above its signal line
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    kst, sig = df["kst"], df["kst_signal"]
    long_x = B.crossed_above(kst, sig)
    short_x = B.crossed_below(kst, sig)
    df["long_entry"] = long_x
    df["short_entry"] = short_x
    df["long_exit"] = short_x
    df["short_exit"] = long_x
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
