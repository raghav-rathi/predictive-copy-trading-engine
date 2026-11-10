"""Pocket pivot signals (Morales & Kacher).

Long entry (long-only): on the same bar, ALL of:
  * UP bar: close > open.
  * Volume test: bar volume exceeds the largest volume of any DOWN bar
    over the previous 240 bars (10 trading days).
  * Close above EMA(240) and EMA(240) above EMA(1200) (constructive
    uptrend / base context).
  * EMA(240) rising (above its value 24 bars ago).
  * Not extended: close < 1.10 * EMA(240).

Long exit: close below EMA(240) (base broken / support lost).
No shorts: short_entry / short_exit are always False.

All inputs are computed from data through bar i's close, so signals on
bar i use no future data. The harness executes at bar i+1's open.
"""

import pandas as pd

EXTENSION_LIMIT = 1.10


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    is_up = df["c"] > df["o"]
    vol_test = df["v"] > df["max_down_vol_240"]
    above_fast = df["c"] > df["ema_240"]
    trend_ok = df["ema_240"] > df["ema_1200"]
    not_extended = df["c"] < EXTENSION_LIMIT * df["ema_240"]
    rising = df["ema_240_rising"].fillna(False)

    entry = (
        is_up
        & vol_test.fillna(False)
        & above_fast.fillna(False)
        & trend_ok.fillna(False)
        & rising
        & not_extended.fillna(False)
    )
    df["long_entry"] = entry.astype(bool)
    df["short_entry"] = False
    df["long_exit"] = (df["c"] < df["ema_240"]).fillna(False).astype(bool)
    df["short_exit"] = False
    return df
