"""Popgun bar-pattern signals.

Long: the close crosses ABOVE the armed popgun high within
the bracket's 5-bar validity. Short: the close crosses
BELOW the armed popgun low within validity. If both triggers
would fire on the same bar, enter NEITHER -- with OHLC data
the intrabar order is unknowable (documented ambiguous-order
rule; with high >= low a single close cannot in practice
cross both levels of one bracket, so the rule is a guard,
not a live path).

Exit: the close goes back below the popgun low that armed a
long (failed popgun), or back above the popgun high that
armed a short; or the opposite entry fires. The house
2xATR hard stop / 3xATR trail sit behind these exits, and
the 48-bar max hold caps a trade that never resolves.

Signal columns are boolean, no NaN, no lookahead
(execution at next-bar open is handled by the harness).
Entries are CROSS-based (crossed_above / crossed_below on
the armed bracket levels), never level conditions: a level
condition would re-fire every bar the close sat beyond the
bracket.
"""

import numpy as np
import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(float)
    armed = df["popgun_armed"].fillna(False).to_numpy(bool)
    long_raw = (
        crossed_above(df["c"], df["popgun_high"]) & armed
    ).fillna(False).to_numpy(bool)
    short_raw = (
        crossed_below(df["c"], df["popgun_low"]) & armed
    ).fillna(False).to_numpy(bool)
    # Ambiguous intrabar order: both triggers on one bar -> neither.
    both = long_raw & short_raw
    long_entry = long_raw & ~both
    short_entry = short_raw & ~both

    popgun_high = df["popgun_high"].to_numpy(float)
    popgun_low = df["popgun_low"].to_numpy(float)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    held_low = None   # popgun low that armed the open long
    held_high = None  # popgun high that armed the open short
    for i in range(n):
        # Exits are judged against levels from entries on earlier bars.
        if held_low is not None and (c[i] < held_low or short_entry[i]):
            long_exit[i] = True
            held_low = None
        if held_high is not None and (c[i] > held_high or long_entry[i]):
            short_exit[i] = True
            held_high = None
        if held_low is None and long_entry[i]:
            held_low = popgun_low[i]
        if held_high is None and short_entry[i]:
            held_high = popgun_high[i]
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
