"""Golden Cross / Death Cross signals, long/short symmetric.

Entry logic (mirror for shorts):

    long_entry  = crossed_above(sma50, sma200)  -- Golden Cross
    short_entry = crossed_below(sma50, sma200)  -- Death Cross

No filters: the cross of a 50-bar average over a 200-bar average
is itself the filter — it cannot fire in chop, because neither
average moves fast enough to cross and re-cross on noise. Adding
a confirmation filter would only delay an already-lagging signal.

Exits are the opposite crosses:

    long_exit  = crossed_below(sma50, sma200)
    short_exit = crossed_above(sma50, sma200)

All conditions read bar-j closes at bar j; the harness executes at
the next bar's open. Signal columns are boolean, no NaN, no
lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast = df["sma50"]
    slow = df["sma200"]

    xup = crossed_above(fast, slow).fillna(False)
    xdn = crossed_below(fast, slow).fillna(False)

    df["long_entry"] = xup.astype(bool)
    df["short_entry"] = xdn.astype(bool)
    df["long_exit"] = xdn.astype(bool)
    df["short_exit"] = xup.astype(bool)
    return df
