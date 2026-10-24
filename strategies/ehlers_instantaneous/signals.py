"""Ehlers Instantaneous Trendline price cross, long/short symmetric.

Entry logic (mirror for shorts):

    long_entry  = crossed_above(close, it)
    short_entry = crossed_below(close, it)

The Instantaneous Trendline is a low-lag smoother, so a close
crossing above it means price has just broken above its own
smoothed trend — a trend-birth signal, not a lagging moving
average cross. No extra filter: the filter's low lag IS the
edge claimed for it, and adding an ADX or slope gate would turn
it into a different strategy. The known cost is whipsaw in chop
(price ping-pongs across any smoother); the ATR stop/trail and
72-bar max hold are the only defences, by design.

Exits are the pure opposite crosses:

    long_exit  = crossed_below(close, it)
    short_exit = crossed_above(close, it)

All conditions read bar-j closes at bar j; the harness executes at
the next bar's open. Signal columns are boolean, no NaN, no
lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    it = df["it"]

    xup = crossed_above(c, it).fillna(False)
    xdn = crossed_below(c, it).fillna(False)

    df["long_entry"] = xup.astype(bool)
    df["short_entry"] = xdn.astype(bool)
    df["long_exit"] = xdn.astype(bool)
    df["short_exit"] = xup.astype(bool)
    return df
