"""CCI extreme mean-reversion signals, long/short symmetric.

Entry logic (mirror for shorts):

    long_entry  = crossed_above(cci, -100)
    short_entry = crossed_below(cci, +100)

The entry is the *return* through the extreme level, not the
touch: a long fires only when CCI climbs back above -100 after
having been below it — the washout is ending, not deepening.
Buying while CCI is still falling through -100 would catch the
falling knife; the cross is what confirms the stretch is
releasing.

Exits are the zero-line crosses in the adverse direction:

    long_exit  = crossed_below(cci, 0)
    short_exit = crossed_above(cci, 0)

A long that has mean-reverted all the way back to CCI = 0 has
done its job; if it then crosses below zero the reversion has
overshot into the other side's territory and the trade is done.
Exits deliberately carry no level filter — once the trade is on,
the zero cross is trigger-happy.

All conditions read bar-j closes at bar j; the harness executes
at the next bar's open. Signal columns are boolean, no NaN, no
lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below
from strategies.cci_extreme.indicators import LONG_LEVEL, SHORT_LEVEL


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cci = df["cci"]

    df["long_entry"] = crossed_above(cci, LONG_LEVEL).fillna(False).astype(bool)
    df["short_entry"] = crossed_below(cci, SHORT_LEVEL).fillna(False).astype(bool)
    df["long_exit"] = crossed_below(cci, 0).fillna(False).astype(bool)
    df["short_exit"] = crossed_above(cci, 0).fillna(False).astype(bool)
    return df
