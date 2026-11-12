"""MACD histogram zero-cross signals.

Long entry:  the MACD histogram crosses above zero (MACD crosses
             above its 9-period signal line).
Short entry: the MACD histogram crosses below zero (MACD crosses
             below its 9-period signal line).
Long exit:   the histogram crosses below zero.
Short exit:  the histogram crosses above zero.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies, so
in practice most positions end on the stop/trail/max-hold before the
opposite cross; the opposite cross is the system-defined exit.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry = B.crossed_above(df["macd_hist"], 0).fillna(False)
    short_entry = B.crossed_below(df["macd_hist"], 0).fillna(False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = short_entry.astype(bool)
    df["short_exit"] = long_entry.astype(bool)
    return df
