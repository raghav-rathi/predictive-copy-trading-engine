"""MESA Sine Wave signals.

Long when sine crosses ABOVE lead_sine (the cycle turning up
near its bottom); short when sine crosses BELOW lead_sine;
exit on the opposite cross. "Lead sine crossing below sine"
is the same event described from the other line, so the long
and short entries are the two directions of one cross.

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry = crossed_above(df["mesa_sine"], df["mesa_lead_sine"]).fillna(False)
    short_entry = crossed_below(df["mesa_sine"], df["mesa_lead_sine"]).fillna(False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
