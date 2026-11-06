"""Shooting star / inverted hammer signals.

Short on a shooting star in an uptrend (close above prior-bar EMA(20)
and 5-bar return above +1%); long on an inverted hammer in a downtrend
(close below prior-bar EMA(20) and 5-bar return below -1%). The pattern
itself is formed by the signal bar's own OHLC, known at its close; the
harness executes at the next bar's open. Exits are the opposite pattern.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ema_prev = df["ema20"].shift(1)
    uptrend = (df["c"] > ema_prev) & (df["ret5"] > 0.01)
    downtrend = (df["c"] < ema_prev) & (df["ret5"] < -0.01)
    df["short_entry"] = (df["shooting_star"] & uptrend).astype(bool)
    df["long_entry"] = (df["inverted_hammer"] & downtrend).astype(bool)
    df["long_exit"] = df["shooting_star"].astype(bool)
    df["short_exit"] = df["inverted_hammer"].astype(bool)
    return df
