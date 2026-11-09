"""Ichimoku Chikou-span cross signals.

Long: close crosses above the close 26 bars ago (the Chikou span
crossing the price as of 26 bars ago, bottom-up). Short: close
crosses below the close 26 bars ago (top-down). Exit a long on the
opposite cross (close below the 26-bar-ago close); exit a short on
the opposite cross. This is a 26-period momentum cross: it is long
exactly when price is above where it was 26 bars ago and the
crossing just happened. All inputs use only data through bar i's
close, so signals on bar i use no future data.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["c"]
    ref = df["chikou_ref"]
    df["long_entry"] = crossed_above(close, ref).fillna(False).astype(bool)
    df["short_entry"] = crossed_below(close, ref).fillna(False).astype(bool)
    df["long_exit"] = crossed_below(close, ref).fillna(False).astype(bool)
    df["short_exit"] = crossed_above(close, ref).fillna(False).astype(bool)
    return df
