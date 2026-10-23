"""Rolling 24-bar VWAP cross signals, long/short symmetric.

Entry logic (mirror for shorts):

    long_entry  = crossed_above(c, vwap) & (vwap_slope > 0) & (vol_ratio > 1.2)
    short_entry = crossed_below(c, vwap) & (vwap_slope < 0) & (vol_ratio > 1.2)

A bare VWAP cross is noise: price ping-pongs across any moving
benchmark in chop. The two filters are the whole strategy:

- vwap_slope > 0 means the rolling benchmark itself is rising —
  buyers are lifting the average transaction price, so the cross
  is a momentum handoff rather than a range flicker. A cross with
  a flat/tilted-down VWAP (the usual whipsaw) is blocked.
- vol_ratio > 1.2 demands the cross print on genuinely heavy
  flow — VWAP is the institutional benchmark (block desks and
  algos target it), so a cross with no volume participation has
  no institutional signal behind it.

Exits are the pure opposite crosses (no filters — once the trade
is on, the exit should be trigger-happy, not gated):

    long_exit  = crossed_below(c, vwap)
    short_exit = crossed_above(c, vwap)

All conditions read bar-j closes at bar j; the harness executes at
the next bar's open. Signal columns are boolean, no NaN, no
lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

VOL_RATIO_MIN = 1.2  # cross must print on 1.2x average volume


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    vwap = df["vwap"]
    slope = df["vwap_slope"]
    vr = df["vol_ratio"]

    xup = crossed_above(c, vwap).fillna(False)
    xdn = crossed_below(c, vwap).fillna(False)
    heavy = (vr > VOL_RATIO_MIN).fillna(False)
    rising = (slope > 0).fillna(False)
    falling = (slope < 0).fillna(False)

    df["long_entry"] = (xup & rising & heavy).astype(bool)
    df["short_entry"] = (xdn & falling & heavy).astype(bool)
    df["long_exit"] = xdn.astype(bool)
    df["short_exit"] = xup.astype(bool)
    return df
