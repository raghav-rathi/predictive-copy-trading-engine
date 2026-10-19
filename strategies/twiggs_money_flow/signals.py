"""Twiggs Money Flow signals.

TMF > 0 means net buying pressure (inflow) over the Wilder window, TMF < 0
net selling pressure (outflow). Long when TMF crosses above the zero line,
short when it crosses below; exit a position when TMF crosses back
through zero against it.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tmf = df["tmf"]
    prev = tmf.shift(1)
    df["long_entry"] = ((prev <= 0) & (tmf > 0)).fillna(False)
    df["short_entry"] = ((prev >= 0) & (tmf < 0)).fillna(False)
    # exit on cross back through zero against the position
    df["long_exit"] = ((prev >= 0) & (tmf < 0)).fillna(False)
    df["short_exit"] = ((prev <= 0) & (tmf > 0)).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
