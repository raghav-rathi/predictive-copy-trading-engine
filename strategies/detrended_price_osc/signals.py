"""Detrended Price Oscillator signals.

Long when DPO crosses above 0, short when DPO crosses below
0, exit on the opposite cross. (StockCharts itself notes DPO
is a cycle-measurement tool, not a momentum-signal tool —
this build trades the zero-line cross anyway, as specified,
and the backtest is the verdict on it.)

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry = crossed_above(df["dpo"], 0).fillna(False)
    short_entry = crossed_below(df["dpo"], 0).fillna(False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
