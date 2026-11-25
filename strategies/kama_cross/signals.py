"""KAMA cross signals.

Long when the fast KAMA crosses above the slow KAMA; short when
it crosses below; exit on the opposite cross. Signal columns are
boolean, no NaN, no lookahead (execution at next-bar open is
handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry = crossed_above(df["kama_fast"], df["kama_slow"]).fillna(False)
    short_entry = crossed_below(df["kama_fast"], df["kama_slow"]).fillna(False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    # exit on the opposite cross: the fast KAMA falling back through
    # the slow one is the trend change
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
