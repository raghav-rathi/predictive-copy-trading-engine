"""Elder SafeZone signals, long/short symmetric.

Entry logic (mirror for shorts):

    long_entry  = crossed_above(c, ema22) & (c > safezone_long)
    short_entry = crossed_below(c, ema22) & (c < safezone_short)

The cross above the EMA(22) is the trend trigger; the SafeZone
condition keeps the entry honest — a long is only taken while
price is still holding above its own trailing stop line, i.e.
the uptrend has not already broken down by Elder's measure.
A cross that prints while price is already below the SafeZone
line is a dead-cat bounce off a broken trend, not a new trend.

Exits are the SafeZone breaks themselves (no EMA condition —
once the trade is on, the line is the arbiter):

    long_exit  = c < safezone_long
    short_exit = c > safezone_short

All conditions read bar-j closes at bar j; the harness executes
at the next bar's open. Signal columns are boolean, no NaN, no
lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    ema = df["ema22"]
    szl = df["safezone_long"]
    szs = df["safezone_short"]

    xup = crossed_above(c, ema).fillna(False)
    xdn = crossed_below(c, ema).fillna(False)

    df["long_entry"] = (xup & (c > szl).fillna(False)).astype(bool)
    df["short_entry"] = (xdn & (c < szs).fillna(False)).astype(bool)
    df["long_exit"] = (c < szl).fillna(False).astype(bool)
    df["short_exit"] = (c > szs).fillna(False).astype(bool)
    return df
