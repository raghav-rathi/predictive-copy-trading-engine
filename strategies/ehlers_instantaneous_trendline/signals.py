"""Ehlers Instantaneous Trendline signals.

Long entry:  close crosses above the Instantaneous Trendline.
Short entry: close crosses below the Instantaneous Trendline.
Long exit:   close crosses below the trendline.
Short exit:  close crosses above the trendline.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies, so
in practice most positions end on the stop/trail/max-hold before the
opposite cross; the opposite cross is the system-defined exit.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import numpy as np
import pandas as pd

from strategies import base as B

# A cross must be a real price move, not floating-point dust: the
# Ehlers recursion on a perfectly flat series leaves the trendline
# ~1e-14 above/below the price, which a strict comparison reads as a
# cross. Requiring the close/trendline gap to exceed 1e-9 of the
# trendline's magnitude (about $0.0001 on a $100k coin) suppresses
# only sub-tick float noise; every genuine cross is orders of
# magnitude larger.
EPS_REL = 1e-9


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    gap = df["c"] - df["it"]
    tol = EPS_REL * df["it"].abs().clip(lower=1.0)
    long_entry = ((gap > tol) & (gap.shift(1) <= tol)).fillna(False)
    short_entry = ((gap < -tol) & (gap.shift(1) >= -tol)).fillna(False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = short_entry.astype(bool)
    df["short_exit"] = long_entry.astype(bool)
    return df
