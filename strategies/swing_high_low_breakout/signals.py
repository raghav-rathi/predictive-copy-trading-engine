"""Swing-structure breakout signals.

Long entry:  close breaks above the last swing high AND the last
             two swing lows are ascending (higher low formed).
Short entry: close breaks below the last swing low AND the last
             two swing highs are descending (lower high formed).
Long exit:   close breaks below the last swing low.
Short exit:  close breaks above the last swing high.

This is a pure structure breakout: the entry fires on the break
itself, not on a pullback to the broken level (that is the
support_resistance_flip strategy). The harness risk layer's
2xATR stop / 2.5xATR trail also applies. Signal columns are
boolean, no NaN, no lookahead (the harness executes at the next
bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry = (
        df["long_breakout"] & df["lows_ascending"]
    ).fillna(False).astype(bool)
    short_entry = (
        df["short_breakout"] & df["highs_descending"]
    ).fillna(False).astype(bool)
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = df["short_breakout"].fillna(False).astype(bool)
    df["short_exit"] = df["long_breakout"].fillna(False).astype(bool)
    return df
