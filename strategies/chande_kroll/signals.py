"""Chande & Kroll stop signals.

Entry on a cross of the OPPOSING stop line, gated by SMA21 bias:
  Long  when close crosses above short_stop AND close > SMA21
  Short when close crosses below long_stop  AND close < SMA21
Exit on a cross of the OWN line (the lines are the trailing stops):
  Exit long  when close crosses below long_stop
  Exit short when close crosses above short_stop
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    long_stop = df["long_stop"]
    short_stop = df["short_stop"]
    sma21 = df["sma21"]
    df["long_entry"] = B.crossed_above(c, short_stop) & (c > sma21)
    df["short_entry"] = B.crossed_below(c, long_stop) & (c < sma21)
    df["long_exit"] = B.crossed_below(c, long_stop)
    df["short_exit"] = B.crossed_above(c, short_stop)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
