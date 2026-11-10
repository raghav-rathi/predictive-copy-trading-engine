"""Fisher ACD signals.

Long entry: close crosses above A-up AND close is above the daily pivot.
Short entry: close crosses below A-down AND close is below the daily pivot.
Exits (B points): exit long on close below the OR low, exit short on
close above the OR high. Failed A-up: close below C-down exits a long
and reverses to short (short_entry set on that bar too); close above
C-up exits a short and reverses to long (long_entry set too).

No entries on the first bar of the UTC day (day_index == 0): the OR bar
itself cannot be traded because the OR is only formed at its close.
Exits are not gated — a position held overnight may exit on any bar.

All inputs are computed from data through bar i's close, so signals on
bar i use no future data. The harness executes at bar i+1's open.
"""

import numpy as np
import pandas as pd

from strategies.base import crossed_above, crossed_below

MS_PER_DAY = 86_400_000


def _day_index(df: pd.DataFrame) -> pd.Series:
    """0-based position of each bar within its UTC day."""
    if "day_index" in df.columns:
        return df["day_index"].astype(int)
    if "t" in df.columns:
        t = df["t"].to_numpy(dtype=np.int64)
        day = pd.Series(t // MS_PER_DAY, index=df.index)
        return df.groupby(day).cumcount().astype(int)
    return pd.Series(np.ones(len(df), dtype=int), index=df.index)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    day_index = _day_index(df)
    can_enter = day_index >= 1

    cross_up = crossed_above(c, df["a_up"])
    cross_down = crossed_below(c, df["a_down"])

    # A-point entries with the daily-pivot filter.
    long_entry = (cross_up & (c > df["pivot_prev_day"]) & can_enter).fillna(False)
    short_entry = (cross_down & (c < df["pivot_prev_day"]) & can_enter).fillna(False)

    # Failed A-point reversals: a close beyond the far C level reverses
    # the trade outright (no pivot filter — the C break is itself the
    # directional signal). See CALIBRATION.md.
    long_entry = long_entry | ((c > df["c_up"]) & can_enter).fillna(False)
    short_entry = short_entry | ((c < df["c_down"]) & can_enter).fillna(False)

    # B-point exits at the OR edges (the C level sits beyond the OR edge,
    # so the C condition is subsumed for the exit itself but kept explicit).
    long_exit = ((c < df["or_low"]) | (c < df["c_down"])).fillna(False)
    short_exit = ((c > df["or_high"]) | (c > df["c_up"])).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
