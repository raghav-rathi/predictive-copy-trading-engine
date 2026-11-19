"""Value-area breakout signals.

Long entry:  the 2nd consecutive close above VAH (acceptance
             above the prior day's value area) — long_trigger.
Short entry: the 2nd consecutive close below VAL — short_trigger.
Long exit:   a close back at or below VAH (rejection into the
             value area, or opposite acceptance below VAL).
Short exit:  a close back at or above VAL.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_trig = df["long_trigger"].fillna(False).astype(bool)
    short_trig = df["short_trigger"].fillna(False).astype(bool)
    df["long_entry"] = long_trig
    df["short_entry"] = short_trig
    df["long_exit"] = (df["c"] <= df["vah"]).fillna(False).astype(bool)
    df["short_exit"] = (df["c"] >= df["val"]).fillna(False).astype(bool)
    return df
