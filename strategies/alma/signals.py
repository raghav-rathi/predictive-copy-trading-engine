"""ALMA dual-cross signals with a 20-bar breakout confirmation.

Long entry: ALMA(9) crosses above ALMA(21) AND the close is a new
20-bar high (close >= rolling(20).max() — current bar included).
Short entry: ALMA(9) crosses below ALMA(21) AND the close is a new
20-bar low. The breakout filter keeps the cross from firing mid-chop:
the fast/slow cross alone whipsaws in a range; requiring a fresh
extreme says momentum actually left the box.

Exits are pure cross-based (no breakout condition): long exits when
the fast line crosses back below the slow, short exits on the reverse
cross.

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

BREAKOUT_N = 20


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast = df["alma_fast"]
    slow = df["alma_slow"]
    cross_up = crossed_above(fast, slow).fillna(False)
    cross_dn = crossed_below(fast, slow).fillna(False)

    new_high = (
        df["c"] >= df["c"].rolling(BREAKOUT_N, min_periods=BREAKOUT_N).max()
    ).fillna(False)
    new_low = (
        df["c"] <= df["c"].rolling(BREAKOUT_N, min_periods=BREAKOUT_N).min()
    ).fillna(False)

    long_entry = (cross_up & new_high).fillna(False)
    short_entry = (cross_dn & new_low).fillna(False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
