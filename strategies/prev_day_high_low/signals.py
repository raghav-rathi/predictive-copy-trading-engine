"""Prior UTC-day high/low breakout signals.

    long_entry  -- 1h close above the prior UTC-day high + 0.1%
                   filter, on a day whose range clears the filter
    short_entry -- 1h close below the prior UTC-day low - 0.1%
                   filter, on a day whose range clears the filter
    long_exit   -- 1h close back inside the prior-day range (below
                   the prior-day high), or the opposite level breaks,
                   or the first bar of a new UTC day (midnight flat)
    short_exit  -- mirror image

Execution note (harness deviation, documented): the midnight-flat
exit is generated on the first bar of the new UTC day and the
harness executes it at the *next* bar's open, so the position is
flat one bar into the new day rather than exactly at midnight.

Caveat (by design): crypto has no true session close, so the UTC
boundary is arbitrary and narrow-range days whipsaw -- the range
filter exists to cut the worst of that, not to cure it.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

FILTER = 0.001  # shipped: 0.1% breakout filter


def add_signals(df: pd.DataFrame, filt: float = FILTER) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    pdh = df["pdh"]
    pdl = df["pdl"]
    ok = df["range_ok"].fillna(False)
    new_day = df["is_new_day"].fillna(False)

    long_level = pdh * (1 + filt)
    short_level = pdl * (1 - filt)

    long_entry = (crossed_above(c, long_level) & ok).fillna(False)
    short_entry = (crossed_below(c, short_level) & ok).fillna(False)
    # back inside the range == close below pdh (long) / above pdl
    # (short); the opposite-level break is subsumed by that test
    long_exit = ((c < pdh) | new_day).fillna(False)
    short_exit = ((c > pdl) | new_day).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
