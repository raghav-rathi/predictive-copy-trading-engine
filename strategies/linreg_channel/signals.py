"""Regression-channel mean-reversion signals.

long_entry  = tag of the lower band with a close back inside (rejection)
short_entry = tag of the upper band with a close back inside
long_exit   = touch of the LSMA midline OR tag of the upper band
short_exit  = touch of the LSMA midline OR tag of the lower band
Execution next-bar-open per the harness contract.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tl, th = df["tag_low"].fillna(False), df["tag_high"].fillna(False)
    mid_touch_up = (df["h"] >= df["lr_lsma"]).fillna(False)
    mid_touch_dn = (df["l"] <= df["lr_lsma"]).fillna(False)
    df["long_entry"] = tl.astype(bool)
    df["short_entry"] = th.astype(bool)
    df["long_exit"] = (mid_touch_up | th).astype(bool)
    df["short_exit"] = (mid_touch_dn | tl).astype(bool)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
