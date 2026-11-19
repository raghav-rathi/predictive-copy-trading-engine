"""Turn-of-the-month signals.

Long-only: long_entry on the first bar of the last calendar day
of each month (00:00 UTC bar; fills at the next bar's open),
long_exit on the 23:00 UTC bar of the 3rd calendar day of the
next month (fills at the 00:00 UTC open of day 4). No shorts:
short_entry and short_exit are always False.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    df["long_entry"] = df["tom_entry"].fillna(False).astype(bool)
    df["short_entry"] = pd.Series(np.zeros(n, dtype=bool), index=df.index)
    df["long_exit"] = df["tom_exit"].fillna(False).astype(bool)
    df["short_exit"] = pd.Series(np.zeros(n, dtype=bool), index=df.index)
    return df
