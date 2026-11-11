"""Connors Cumulative RSI signals (Connors & Alvarez).

  Long entry:  cum_rsi crosses above -100 from below.
  Short entry: cum_rsi crosses below +100 from above.
  Long exit:   cum_rsi crosses above 0.
  Short exit:  cum_rsi crosses below 0.

All inputs are computed from data through bar i's close, so signals on
bar i use no future data. The harness executes at bar i+1's open.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

LONG_ENTRY_LEVEL = -100.0
SHORT_ENTRY_LEVEL = 100.0
EXIT_LEVEL = 0.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cum = df["cum_rsi"]
    df["long_entry"] = crossed_above(cum, LONG_ENTRY_LEVEL).fillna(False).astype(bool)
    df["short_entry"] = crossed_below(cum, SHORT_ENTRY_LEVEL).fillna(False).astype(bool)
    df["long_exit"] = crossed_above(cum, EXIT_LEVEL).fillna(False).astype(bool)
    df["short_exit"] = crossed_below(cum, EXIT_LEVEL).fillna(False).astype(bool)
    return df
