"""Ehlers Center of Gravity signals.

Long entry:  CG crosses up through trigger (transition only).
Short entry: CG crosses down through trigger (transition only).
Long exit:   CG crosses down through trigger.
Short exit:  CG crosses up through trigger.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cg = df["cg"]
    tr = df["cg_trigger"]
    prev_cg = cg.shift(1)
    prev_tr = tr.shift(1)
    cross_up = ((cg > tr) & (prev_cg <= prev_tr)).fillna(False).astype(bool)
    cross_down = ((cg < tr) & (prev_cg >= prev_tr)).fillna(False).astype(bool)
    df["long_entry"] = cross_up
    df["short_entry"] = cross_down
    df["long_exit"] = cross_down
    df["short_exit"] = cross_up
    return df
