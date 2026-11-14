"""Fibonacci cluster bounce signals.

A cluster is a confluence zone: >= 2 Fibonacci retracement levels
from different swings inside 0.5x ATR. Trade the bounce off it:

    long_entry  = low touches the nearest support cluster (within
                  0.25x ATR) and the bar closes back above it, after
                  the previous close was still above the cluster
                  (a genuine dip-and-bounce, not a reclaim from below)
    short_entry = high touches the nearest resistance cluster
                  (within 0.25x ATR) and the bar closes back below
                  it, after the previous close was still below it

Exits are the touch of the opposite cluster (same bounce logic):
a long exits when price taps a resistance cluster and closes back
below it; a short exits on a support-cluster tap that closes back
above. The 2xATR stop / 3xATR trail / 200-bar max hold in risk.py
cover the cases where price slices straight through a cluster.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

TOUCH_ATR = 0.25  # touch tolerance in ATR multiples


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    atr = df["atr"]
    tol = TOUCH_ATR * atr

    sup = df["fib_sup"]
    res = df["fib_res"]
    lo = df["l"]
    hi = df["h"]
    cl = df["c"]
    prev_cl = cl.shift(1)

    long_entry = (
        (lo - sup).abs().fillna(1e18) <= tol
    ) & (cl > sup) & (prev_cl > sup)
    short_entry = (
        (hi - res).abs().fillna(1e18) <= tol
    ) & (cl < res) & (prev_cl < res)

    long_exit = (
        (hi - res).abs().fillna(1e18) <= tol
    ) & (cl < res)
    short_exit = (
        (lo - sup).abs().fillna(1e18) <= tol
    ) & (cl > sup)

    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = long_exit.fillna(False).astype(bool)
    df["short_exit"] = short_exit.fillna(False).astype(bool)
    return df
