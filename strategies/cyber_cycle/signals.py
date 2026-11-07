"""Cyber Cycle signals.

Long when the Signal line crosses above its own 1-bar-delayed value
(Signal[i] > Signal[i-1] and Signal[i-1] <= Signal[i-2]); short on the
mirror cross below. Exit on the reverse cross. All comparisons use
only data through bar i's close — no lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sig = df["cc_signal"]
    delayed = sig.shift(1)
    long_entry = B.crossed_above(sig, delayed)
    short_entry = B.crossed_below(sig, delayed)
    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = df["short_entry"].copy()
    df["short_exit"] = df["long_entry"].copy()
    return df
