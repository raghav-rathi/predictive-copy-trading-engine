"""Livermore trend-system signals (Jesse Livermore).

Long: close breaks above the prior 20-bar high AND the swing
lows are rising (the 10-bar low ending 10 bars ago is higher
than the 10-bar low ending 20 bars ago) — a breakout with
higher lows behind it, i.e. an uptrend by Livermore's
definition, not a lone spike.

Short mirror: close breaks below the prior 20-bar low AND the
swing highs are falling (lower highs).

Exit long when close breaks below the prior 10-bar low; exit
short when close breaks above the prior 10-bar high — the
trend structure itself failing. Signal columns are boolean,
no NaN, no lookahead (execution at next-bar open is handled
by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry = (
        (df["c"] > df["brk_high"]) & df["higher_lows"].fillna(False)
    ).fillna(False)
    short_entry = (
        (df["c"] < df["brk_low"]) & df["lower_highs"].fillna(False)
    ).fillna(False)
    long_exit = crossed_below(df["c"], df["exit_low"]).fillna(False)
    short_exit = crossed_above(df["c"], df["exit_high"]).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
