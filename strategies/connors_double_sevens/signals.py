"""Connors Double 7s signals (long-only).

Evaluated once per UTC day, on that day's last 1h bar (the 23:00 UTC
bar, whose close is the day's close). The harness executes at the
next bar's open (00:00 UTC, next day), which matches the system's
"buy on the close".

  Long entry: the daily close is the lowest daily close of the last
    7 days (incl. today) AND the daily close is above the 200-day
    SMA of daily closes.
  Long exit: the daily close is the highest daily close of the last
    7 days (incl. today).

No short signals: the original system is long-only. The original
system has no stop loss and no target; the exit is purely the
7-day-high close (the 10x ATR stop in risk.py is a harness
formality, not part of the system).

All inputs are known by the signal bar's close, so signals on bar i
use no future data.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    on_day_close = df["is_day_close"].fillna(False)
    is_low7 = (df["c"] == df["low7_daily"]).fillna(False)
    above_sma200 = (df["c"] > df["sma200_daily"]).fillna(False)
    is_high7 = (df["c"] == df["high7_daily"]).fillna(False)

    df["long_entry"] = (on_day_close & is_low7 & above_sma200).astype(bool)
    df["short_entry"] = pd.Series(False, index=df.index, dtype=bool)
    df["long_exit"] = (on_day_close & is_high7).astype(bool)
    df["short_exit"] = pd.Series(False, index=df.index, dtype=bool)
    return df
