"""SMI Ergodic signals (signal-line cross + zero-line regime filter).

long_entry  = SMI crosses above its signal line while SMI > 0
short_entry = SMI crosses below its signal line while SMI < 0
long_exit   = SMI crosses back below its signal line
short_exit  = SMI crosses back above its signal line
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    smi, sig = df["smi"], df["smi_signal"]
    long_x = B.crossed_above(smi, sig) & (smi > 0)
    short_x = B.crossed_below(smi, sig) & (smi < 0)
    df["long_entry"] = long_x
    df["short_entry"] = short_x
    df["long_exit"] = B.crossed_below(smi, sig)
    df["short_exit"] = B.crossed_above(smi, sig)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
