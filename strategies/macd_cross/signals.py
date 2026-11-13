"""MACD signal-line crossover signals (Gerald Appel, 1979).

Long entry:  MACD line crosses above its signal line.
Short entry: MACD line crosses below its signal line.
Long exit:   MACD line crosses below its signal line (the opposite
             cross).
Short exit:  MACD line crosses above its signal line.

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
    macd = df["macd"]
    sig = df["macd_signal"]
    long_entry = B.crossed_above(macd, sig)
    short_entry = B.crossed_below(macd, sig)
    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = short_entry.fillna(False).astype(bool)
    df["short_exit"] = long_entry.fillna(False).astype(bool)
    return df
