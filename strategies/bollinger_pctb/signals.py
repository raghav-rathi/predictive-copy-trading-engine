"""Bollinger %B signals, long/short symmetric.

Entry logic (mirror for shorts):

    long_entry  = crossed_above(pctb, 0)   -- %B reclaims the lower band
    short_entry = crossed_below(pctb, 1)   -- %B loses the upper band

A %B cross of 0 means price has tagged the lower band and come back
inside it: the tag itself is capitulation, the reclaim is the trade.
Trading the tag directly (buying at %B < 0) catches falling knives;
waiting for the cross above 0 demands the reclaim first. The mirror
holds for shorts at the upper band.

Exits are the mid-band (0.5) crosses — the mean-reversion leg has
run its course once price is back to the middle of the band:

    long_exit  = crossed_below(pctb, 0.5)
    short_exit = crossed_above(pctb, 0.5)

All conditions read bar-j closes at bar j; the harness executes at
the next bar's open. Signal columns are boolean, no NaN, no
lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pctb = df["pctb"]

    xup0 = crossed_above(pctb, 0).fillna(False)
    xdn1 = crossed_below(pctb, 1).fillna(False)
    xdn05 = crossed_below(pctb, 0.5).fillna(False)
    xup05 = crossed_above(pctb, 0.5).fillna(False)

    df["long_entry"] = xup0.astype(bool)
    df["short_entry"] = xdn1.astype(bool)
    df["long_exit"] = xdn05.astype(bool)
    df["short_exit"] = xup05.astype(bool)
    return df
