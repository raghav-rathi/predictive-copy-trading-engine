"""Price-Volume Trend signals (Granville).

Entries: PVT crosses its own moving average — buying/selling pressure
turning faster than its recent baseline.
  long_entry:  PVT crosses above SMA20(PVT)
  short_entry: PVT crosses below SMA20(PVT)
Exits: the opposite cross (pressure regime flipped).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pvt = df["pvt"]
    ma = df["pvt_ma"]
    df["long_entry"] = B.crossed_above(pvt, ma).fillna(False)
    df["short_entry"] = B.crossed_below(pvt, ma).fillna(False)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
