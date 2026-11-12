"""Stochastic Momentum Index signals (William Blau, 1995).

Long entry:  SMI crosses up through -40 (out of the oversold zone).
Short entry: SMI crosses down through +40 (out of the overbought zone).
Long exit:   SMI crosses back below 0 (momentum flips to the lower
             half of the range).
Short exit:  SMI crosses back above 0.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies, so
in practice most positions end on the stop/trail/max-hold before the
zero-line exit; the zero-line cross is the system-defined exit.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    smi = df["smi"]
    long_entry = B.crossed_above(smi, -40.0)
    short_entry = B.crossed_below(smi, 40.0)
    long_exit = B.crossed_below(smi, 0.0)
    short_exit = B.crossed_above(smi, 0.0)
    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = long_exit.fillna(False).astype(bool)
    df["short_exit"] = short_exit.fillna(False).astype(bool)
    return df
