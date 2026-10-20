"""Kalman filter trend signals.

Entry needs BOTH a cross and slope confirmation:
  long_entry  -- close crosses above kf AND kf_slope > 0
  short_entry -- close crosses below kf AND kf_slope < 0

The cross alone whipsaws on filter touch-and-go; requiring the filter
itself to already be moving in the trade's direction filters out the
flat-chop taps where the filter is stationary.

Exits are the bare opposite crosses (no slope condition): once the
close crosses back through the filter estimate, the premise is dead
and the strategy hands the position back to the risk layer (2xATR stop
/ 200-bar max hold).

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    kf = df["kf"]
    slope = df["kf_slope"].fillna(0.0)
    up = crossed_above(c, kf).fillna(False)
    dn = crossed_below(c, kf).fillna(False)
    df["long_entry"] = (up & (slope > 0)).astype(bool)
    df["short_entry"] = (dn & (slope < 0)).astype(bool)
    df["long_exit"] = dn.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
