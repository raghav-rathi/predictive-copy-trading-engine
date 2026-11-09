"""TPO value-area breakout signals.

Long: close crosses above VAH (value-area high). Short: close
crosses below VAL (value-area low). Exit a long on a close breaking
below VAL (opposite value-area break); exit a short on a close
breaking above VAH. This is a breakout of the value area, not a
fade of its edges: price is expected to run once value is accepted
outside the 70% TPO band. All levels use only data through bar i's
close, so signals on bar i use no future data.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["c"]
    vah = df["tpo_vah"]
    val = df["tpo_val"]
    df["long_entry"] = crossed_above(close, vah).fillna(False).astype(bool)
    df["short_entry"] = crossed_below(close, val).fillna(False).astype(bool)
    df["long_exit"] = crossed_below(close, val).fillna(False).astype(bool)
    df["short_exit"] = crossed_above(close, vah).fillna(False).astype(bool)
    return df
