"""Dual Momentum signals (Gary Antonacci, 2014).

Ranking is by relative momentum (``rel_mom``); the runner attaches
``mom_rank`` (1 = highest rel_mom) and ``n_coins`` to each coin's
frame. A coin qualifies long only while it is the top-ranked coin
AND its absolute momentum is positive; it qualifies short only
while it is the bottom-ranked coin AND its absolute momentum is
negative; otherwise the system is flat in that coin.

    qual_long  = (mom_rank == 1) & (abs_mom > 0)
    qual_short = (mom_rank == n_coins) & (abs_mom < 0)

Entries fire on the bar the coin first qualifies (state change);
exits fire on any bar the coin stops qualifying (rank flip, or
absolute momentum turning against the position). The harness
executes at the next bar's open, and its 2xATR stop / 2.5xATR
trail / 120-bar max hold also apply.

Signal columns are boolean, no NaN, no lookahead. When
``mom_rank`` / ``n_coins`` are absent (standalone single-coin use),
the coin is treated as rank 1 of 1, so only the absolute-momentum
leg applies.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    abs_mom = df["abs_mom"]
    if "mom_rank" in df.columns:
        rank = df["mom_rank"]
    else:
        rank = pd.Series(1, index=df.index)
    if "n_coins" in df.columns:
        n_coins = df["n_coins"]
    else:
        n_coins = pd.Series(1, index=df.index)
    top = (rank == 1).fillna(False)
    bottom = (rank == n_coins).fillna(False)
    qual_long = (top & (abs_mom > 0)).fillna(False)
    qual_short = (bottom & (abs_mom < 0)).fillna(False)
    prev_long = qual_long.shift(1).fillna(False).astype(bool)
    prev_short = qual_short.shift(1).fillna(False).astype(bool)
    df["long_entry"] = (qual_long & ~prev_long).astype(bool)
    df["short_entry"] = (qual_short & ~prev_short).astype(bool)
    df["long_exit"] = (~qual_long).astype(bool)
    df["short_exit"] = (~qual_short).astype(bool)
    return df
