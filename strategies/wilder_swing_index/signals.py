"""Wilder Swing Index / ASI signals.

Long when the ASI breaks above its prior 20-bar high (ASI > rolling max of
the previous 20 ASI values, current bar excluded); short when it breaks
below its prior 20-bar low. Exits on the opposite break. Risk-level exits
(stop, max hold) come from risk.py.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    asi = df["asi"]
    break_up = (asi > df["asi_prior_high"]).fillna(False)
    break_dn = (asi < df["asi_prior_low"]).fillna(False)
    df["break_up"] = break_up
    df["break_dn"] = break_dn
    df["long_entry"] = break_up
    df["short_entry"] = break_dn
    df["long_exit"] = break_dn
    df["short_exit"] = break_up
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
