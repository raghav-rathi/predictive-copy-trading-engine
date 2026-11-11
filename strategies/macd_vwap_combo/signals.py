"""MACD + session VWAP signals.

  Long entry:  MACD line crosses above its signal line while
               close > session VWAP.
  Short entry: MACD line crosses below its signal line while
               close < session VWAP.
  Long exit:   MACD line crosses below its signal line.
  Short exit:  MACD line crosses above its signal line.

The VWAP gates entries only: exits fire on the opposite MACD cross
regardless of where price sits vs VWAP.

All inputs are computed from data through bar i's close, so signals on
bar i use no future data. The harness executes at bar i+1's open.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = crossed_above(df["macd"], df["macd_signal"]).fillna(False)
    cross_dn = crossed_below(df["macd"], df["macd_signal"]).fillna(False)
    above_vwap = (df["c"] > df["vwap_day"]).fillna(False)
    below_vwap = (df["c"] < df["vwap_day"]).fillna(False)
    df["long_entry"] = (cross_up & above_vwap).astype(bool)
    df["short_entry"] = (cross_dn & below_vwap).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
