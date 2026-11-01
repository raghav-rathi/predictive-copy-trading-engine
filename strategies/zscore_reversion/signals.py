"""Z-score mean-reversion signals.

    long_entry  -- z-score crosses below -2 (stretched down)
    short_entry -- z-score crosses above +2 (stretched up)
    long_exit   -- z-score crosses above 0 (reverted to the mean)
    short_exit  -- z-score crosses below 0 (reverted to the mean)

Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies import base as B

ENTRY = 2.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    le = B.crossed_below(df["zscore"], -ENTRY).fillna(False)
    se = B.crossed_above(df["zscore"], ENTRY).fillna(False)
    lx = B.crossed_above(df["zscore"], 0.0).fillna(False)
    sx = B.crossed_below(df["zscore"], 0.0).fillna(False)
    df["long_entry"] = le.astype(bool)
    df["short_entry"] = se.astype(bool)
    df["long_exit"] = lx.astype(bool)
    df["short_exit"] = sx.astype(bool)
    return df
