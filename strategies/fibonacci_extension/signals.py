"""Retracement-zone turn entries; SMA50 cross exits."""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = (df["c"] > df["sma50"]) & (df["sma50"] > df["sma50"].shift(5))
    down = (df["c"] < df["sma50"]) & (df["sma50"] < df["sma50"].shift(5))
    zone = (df["fib_retr"] >= 0.382) & (df["fib_retr"] <= 0.618)
    long_e = up & zone & (df["c"] > df["c"].shift(1))
    short_e = down & zone & (df["c"] < df["c"].shift(1))
    # for shorts the retracement is measured from the low: mirror zone
    retr_down = (df["c"] - df["fib_low"]) / (df["fib_high"] - df["fib_low"])
    short_e = down & (retr_down >= 0.382) & (retr_down <= 0.618) & (df["c"] < df["c"].shift(1))
    df["long_entry"] = long_e.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = short_e.fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = B.crossed_below(df["c"], df["sma50"]).fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = B.crossed_above(df["c"], df["sma50"]).fillna(False).to_numpy(dtype=bool)
    return df
