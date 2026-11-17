"""Break-and-retest / role-reversal signals.

Long entry:  retest-hold bar after a broken resistance level
             (low within 0.5x ATR of the level, close back above it).
Short entry: retest-hold bar after a broken support level
             (low within 0.5x ATR of the level, close back below it).
Long exit:   close back below the flipped level.
Short exit:  close back above the flipped level.

The entry is the retest, not the break: a break with no retest
within 20 bars expires with no trade. The harness risk layer's
2xATR stop / 2.5xATR trail also applies. Signal columns are
boolean, no NaN, no lookahead (the harness executes at the next
bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = df["retest_bull"].fillna(False).astype(bool)
    df["short_entry"] = df["retest_bear"].fillna(False).astype(bool)
    df["long_exit"] = (
        df["flip_long_level"].notna() & (df["c"] < df["flip_long_level"])
    ).fillna(False).astype(bool)
    df["short_exit"] = (
        df["flip_short_level"].notna() & (df["c"] > df["flip_short_level"])
    ).fillna(False).astype(bool)
    return df
