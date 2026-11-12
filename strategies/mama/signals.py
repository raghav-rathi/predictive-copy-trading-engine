"""MAMA signals.

Long entry:  MAMA crosses above FAMA.
Short entry: MAMA crosses below FAMA.
Long exit:   MAMA crosses below FAMA (opposite cross).
Short exit:  MAMA crosses above FAMA (opposite cross).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies, so
in practice most positions end on the stop/trail/max-hold before the
opposite cross; the opposite cross is the system-defined exit.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_cross = B.crossed_above(df["mama"], df["fama"]).fillna(False)
    short_cross = B.crossed_below(df["mama"], df["fama"]).fillna(False)
    df["long_entry"] = long_cross.astype(bool)
    df["short_entry"] = short_cross.astype(bool)
    df["long_exit"] = short_cross.astype(bool)
    df["short_exit"] = long_cross.astype(bool)
    return df
