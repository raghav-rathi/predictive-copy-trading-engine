"""UT Bot Alerts signals.

Buy signal = close crosses above the trailing stop (the stop
flips from above price to below it); sell signal = close
crosses below the stop. Long on buy, short on sell; exit on the
opposite signal. Signal columns are boolean, no NaN, no
lookahead (execution at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry = crossed_above(df["c"], df["ut_stop"]).fillna(False)
    short_entry = crossed_below(df["c"], df["ut_stop"]).fillna(False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    # exit on the opposite signal: the stop flipping is the trend change
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
