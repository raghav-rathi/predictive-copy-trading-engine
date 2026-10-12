"""Money Flow Index signals: classic 20/80 reversal rules.

long_entry  = MFI crosses above OS (20) from below
short_entry = MFI crosses below OB (80) from above
long_exit   = MFI touches the opposite extreme (>= OB 80)
short_exit  = MFI touches the opposite extreme (<= OS 20)

The exit is the classic "take the money-flow extreme" rule: a long is
not held past overbought money flow. Execution is next-bar-open per the
harness contract.
"""

import pandas as pd

OS = 20.0
OB = 80.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    mfi = df["mfi"]
    prev = mfi.shift(1)
    df["long_entry"] = (mfi > OS) & (prev <= OS)
    df["short_entry"] = (mfi < OB) & (prev >= OB)
    df["long_exit"] = mfi >= OB
    df["short_exit"] = mfi <= OS
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
