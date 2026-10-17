"""HalfTrend signals.

long_entry  = trend flips from down (-1) to up (+1)
short_entry = trend flips from up (+1) to down (-1)
long_exit   = trend flips back to -1
short_exit  = trend flips back to +1
The line itself doubles as the trailing reference; the harness hard
stop + chandelier trail are set from the same ATR(100) scale.
Execution next-bar-open per the harness contract.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = df["halftrend_dir"]
    prev = d.shift(1)
    flip_up = (d == 1.0) & (prev == -1.0)
    flip_dn = (d == -1.0) & (prev == 1.0)
    df["long_entry"] = flip_up.fillna(False)
    df["short_entry"] = flip_dn.fillna(False)
    df["long_exit"] = flip_dn.fillna(False)
    df["short_exit"] = flip_up.fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
