"""Keltner pullback signals.

    long_entry  -- close crosses back above the Keltner midline
                   while price is above a rising EMA50 (a pullback
                   to the midline in an uptrend, rejoining)
    short_entry -- close crosses back below the Keltner midline
                   while price is below a falling EMA50
    long_exit   -- close crosses back below the midline (the
                   pullback thesis has failed a second time)
    short_exit  -- close crosses back above the midline

The cross itself guarantees a pullback happened: the close was
on the far side of the midline on the prior bar. Boolean
columns, no NaN, no lookahead (all inputs use only bars
through the current close).
"""

import numpy as np
import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    mid = df["kc_mid"]
    cross_up = crossed_above(c, mid).fillna(False)
    cross_dn = crossed_below(c, mid).fillna(False)
    trend_up = (c > df["ema50"]) & df["ema50_up"]
    trend_dn = (c < df["ema50"]) & df["ema50_dn"]
    df["long_entry"] = (cross_up & trend_up).fillna(False).astype(bool)
    df["short_entry"] = (cross_dn & trend_dn).fillna(False).astype(bool)
    df["long_exit"] = cross_dn.fillna(False).astype(bool)
    df["short_exit"] = cross_up.fillna(False).astype(bool)
    return df
