"""Stochastic-hook signals.

Long: slowK crosses above its trigger AND slowK rising AND rawK rising
AND up-trend bias (close above EMA50). Short: mirror.
Exit: stochastic crosses against the position (crossed_below exits a
long, crossed_above exits a short). Stop / max-hold from risk.py.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = B.crossed_above(df["slowK"], df["trig"]).fillna(False)
    cross_dn = B.crossed_below(df["slowK"], df["trig"]).fillna(False)
    df["long_entry"] = (
        cross_up & df["slowK_rising"] & df["rawK_rising"] & df["bias_up"]
    ).fillna(False)
    df["short_entry"] = (
        cross_dn & (~df["slowK_rising"]) & (~df["rawK_rising"]) & df["bias_dn"]
    ).fillna(False)
    df["long_exit"] = cross_dn
    df["short_exit"] = cross_up
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
