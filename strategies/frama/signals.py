"""FRAMA signals.

long_entry  = close crosses above FRAMA while FRAMA slope > 0 and
              FRAMA above its 100-bar SMA
short_entry = close crosses below FRAMA while FRAMA slope < 0 and
              FRAMA below its 100-bar SMA
long_exit   = close crosses back below FRAMA
short_exit  = close crosses back above FRAMA
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, f, s, slow = df["c"], df["frama"], df["frama_slope"], df["frama_slow"]
    long_x = B.crossed_above(c, f) & (s > 0) & (f > slow)
    short_x = B.crossed_below(c, f) & (s < 0) & (f < slow)
    df["long_entry"] = long_x.fillna(False)
    df["short_entry"] = short_x.fillna(False)
    df["long_exit"] = B.crossed_below(c, f).fillna(False)
    df["short_exit"] = B.crossed_above(c, f).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
