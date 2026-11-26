"""Supertrend + session VWAP agreement signals.

Long: Supertrend is long (direction +1, line below price)
AND the close is above the UTC-day session VWAP. Short:
Supertrend is short (direction -1) AND the close is below
the session VWAP. Exit: Supertrend flips OR the close
crosses the session VWAP against the position (long exits
when the close falls below VWAP, short when it rises above).

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness). The entry is a
level condition, not a cross: while both legs agree the
signal stays true, and the harness (one position at a time,
flat between trades) takes the first bar after going flat.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = df["supertrend_dir"] == 1
    down = df["supertrend_dir"] == -1
    above = df["c"] > df["vwap"]
    below = df["c"] < df["vwap"]
    df["long_entry"] = (up & above).fillna(False).astype(bool)
    df["short_entry"] = (down & below).fillna(False).astype(bool)
    df["long_exit"] = (down | below).fillna(False).astype(bool)
    df["short_exit"] = (up | above).fillna(False).astype(bool)
    return df
