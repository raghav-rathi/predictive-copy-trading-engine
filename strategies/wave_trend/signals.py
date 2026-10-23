"""WaveTrend Oscillator signals — LazyBear's canonical cross-in-zone rules.

    long_entry  = crossed_above(wt1, wt2) & (wt1.shift(1) < -53)
    short_entry = crossed_below(wt1, wt2) & (wt1.shift(1) > 53)
    long_exit   = crossed_below(wt1, wt2) | (wt1 > 60)
    short_exit  = crossed_above(wt1, wt2) | (wt1 < -60)

A signal fires only when the fast oscillator line wt1 crosses the
slow line wt2 *from the oversold/overbought zone*: a cross above
counts as a long only if the prior bar's wt1 sat below -53 (the
bullish reversal out of oversold), and a cross below counts as a
short only if the prior bar's wt1 sat above +53 (the bearish
reversal out of overbought). The zone gate reads the *prior* bar
because wt1's current-bar value belongs to the bar being crossed on
— the canonical TradingView port checks wt1[1] too.

Exits are the mirror: the opposite cross ends the trade early, and
the ±60 extreme lines are hard exits (a wt1 above +60 is exhausted
to the upside for a long; below -60 is exhausted to the downside
for a short).

Signal columns are boolean, no NaN, no lookahead: bar-i signals use
data through bar-i close (the harness executes at the next bar's
open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

OVERSOLD = -53.0   # LazyBear's oversold zone line (canonical)
OVERBOUGHT = 53.0  # LazyBear's overbought zone line (canonical)
LONG_EXTREME = 60.0    # upside exhaustion exit for longs
SHORT_EXTREME = -60.0  # downside exhaustion exit for shorts


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    wt1 = df["wt1"]
    wt2 = df["wt2"]
    up = crossed_above(wt1, wt2).fillna(False)
    dn = crossed_below(wt1, wt2).fillna(False)
    # Prior-bar zone membership: the cross must originate in the zone.
    was_oversold = (wt1.shift(1) < OVERSOLD).fillna(False)
    was_overbought = (wt1.shift(1) > OVERBOUGHT).fillna(False)
    long_extreme = (wt1 > LONG_EXTREME).fillna(False)
    short_extreme = (wt1 < SHORT_EXTREME).fillna(False)
    df["long_entry"] = (up & was_oversold).astype(bool)
    df["short_entry"] = (dn & was_overbought).astype(bool)
    df["long_exit"] = (dn | long_extreme).astype(bool)
    df["short_exit"] = (up | short_extreme).astype(bool)
    return df
