"""Murrey Math extreme-reversal signals.

Long when price touches the bottom zone (0/8 or 1/8) and then closes
back above L1 (reversal off the extreme); short when price touches the
top zone (7/8 or 8/8) and closes back below L7. The touch may have
happened up to ``touch_lookback`` bars earlier -- the entry bar is the
one that reclaims L1 (long) / loses L7 (short).

Exits: long exits at the 4/8 pivot (mid) or on an opposite-extreme
(top-zone) touch; short exits mirror. Signal columns are boolean, no
NaN, no lookahead (execution at next-bar open is handled by the
harness).
"""

import pandas as pd

from strategies import base as B

TOUCH_LOOKBACK = 3


def add_signals(df: pd.DataFrame, touch_lookback: int = TOUCH_LOOKBACK) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    L1 = df["mm_L1"]
    L4 = df["mm_mid"]
    L7 = df["mm_L7"]
    recent_bottom = (
        df["mm_touch_bottom"].rolling(touch_lookback, min_periods=1).max() > 0
    ).fillna(False)
    recent_top = (
        df["mm_touch_top"].rolling(touch_lookback, min_periods=1).max() > 0
    ).fillna(False)
    touch_top_now = df["mm_touch_top"].fillna(False)
    touch_bottom_now = df["mm_touch_bottom"].fillna(False)

    long_entry = (B.crossed_above(c, L1) & recent_bottom).fillna(False)
    short_entry = (B.crossed_below(c, L7) & recent_top).fillna(False)
    long_exit = (B.crossed_above(c, L4) | touch_top_now).fillna(False)
    short_exit = (B.crossed_below(c, L4) | touch_bottom_now).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
