"""Anchored VWAP signals (Shannon's reclaim idea).

  long_entry:  close crosses above the active anchor VWAP, the 5-bar
               VWAP slope is rising, and price spent at least
               RECLAIM_BARS of the last 10 bars below the VWAP (a genuine
               reclaim from a dip, not a graze of the line).
  short_entry: mirror image.

Exits are left to the risk module (2xATR stop, 3xATR trail, 72-bar cap):
once price reclaims the line the engine does not second-guess it.
"""

import pandas as pd

from strategies import base as B

SLOPE_BARS = 5
RECLAIM_WINDOW = 10
RECLAIM_BARS = 2  # minimum bars below the VWAP inside the window


def add_signals(df: pd.DataFrame, reclaim_bars: int = RECLAIM_BARS) -> pd.DataFrame:
    df = df.copy()
    av = df["avwap"]
    cl = df["c"]

    cross_up = B.crossed_above(cl, av)
    cross_dn = B.crossed_below(cl, av)
    slope_up = av.diff(SLOPE_BARS) > 0
    slope_dn = av.diff(SLOPE_BARS) < 0
    below = cl < av
    below_count = below.rolling(RECLAIM_WINDOW, min_periods=RECLAIM_WINDOW).sum()
    reclaim = below_count >= reclaim_bars

    long_sig = (cross_up & slope_up & reclaim).fillna(False).astype(bool)
    short_sig = (cross_dn & slope_dn & reclaim).fillna(False).astype(bool)

    df["long_entry"] = long_sig
    df["short_entry"] = short_sig
    df["long_exit"] = pd.Series(False, index=df.index)
    df["short_exit"] = pd.Series(False, index=df.index)
    return df
