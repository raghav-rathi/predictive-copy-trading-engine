"""VIDYA signals.

long_entry  = close crosses above VIDYA while VIDYA slope > 0 and
              VIDYA above its 50-bar SMA (adaptive trend confirmed up)
short_entry = close crosses below VIDYA while VIDYA slope < 0 and
              VIDYA below its 50-bar SMA
long_exit   = close crosses back below VIDYA
short_exit  = close crosses back above VIDYA
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, v, s, slow = df["c"], df["vidya"], df["vidya_slope"], df["vidya_slow"]
    long_x = B.crossed_above(c, v) & (s > 0) & (v > slow)
    short_x = B.crossed_below(c, v) & (s < 0) & (v < slow)
    df["long_entry"] = long_x.fillna(False)
    df["short_entry"] = short_x.fillna(False)
    df["long_exit"] = B.crossed_below(c, v).fillna(False)
    df["short_exit"] = B.crossed_above(c, v).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
