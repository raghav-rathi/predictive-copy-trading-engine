"""Consecutive up/down days fade signals (Larry Connors).

SHORT: the close completes its 4th consecutive up close
(up_streak crosses above 3 -- fires exactly once per streak).
LONG: the close completes its 4th consecutive down close
(down_streak crosses above 3). The fade bets the streak
mean-reverts; Connors' 1995-2006 study found the
underperformance after 3+ up days (outperformance after 3+
down days) grows with the streak length.

Exit: long exits when the close crosses ABOVE sma10
(reversion to the mean); short exits when the close crosses
BELOW sma10; or the opposite entry fires. The house 2xATR
hard stop / 3xATR trail sit behind these exits, and the
24-bar max hold caps a trade that never reverts.

Signal columns are boolean, no NaN, no lookahead
(execution at next-bar open is handled by the harness).
Entries are CROSS-based (crossed_above on the streak
count), never level conditions: a level condition such as
up_streak >= 4 would re-fire every bar a long streak
persisted.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

STREAK_N = 4


def add_signals(df: pd.DataFrame, streak_n: int = STREAK_N) -> pd.DataFrame:
    df = df.copy()
    short_entry = crossed_above(df["up_streak"], streak_n - 1).fillna(False)
    long_entry = crossed_above(df["down_streak"], streak_n - 1).fillna(False)
    # Ambiguous intrabar order: both triggers on one bar -> neither.
    # (A close cannot be both up and down vs the prior close, so
    # this is a guard, not a live path.)
    both = long_entry & short_entry
    long_entry = long_entry & ~both
    short_entry = short_entry & ~both

    long_exit = crossed_above(df["c"], df["sma10"]).fillna(False) | short_entry
    short_exit = crossed_below(df["c"], df["sma10"]).fillna(False) | long_entry

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
