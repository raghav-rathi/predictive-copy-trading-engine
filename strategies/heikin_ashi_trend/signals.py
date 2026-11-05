"""Heikin Ashi trend signals.

Long after 2 consecutive green HA candles following a red run AND the real
close above EMA(50) of real closes; short mirror. Exit on the first
opposite-colour HA candle. Signals use only data through bar i's close.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    green = df["ha_close"] > df["ha_open"]
    red = df["ha_close"] < df["ha_open"]
    two_green = green & green.shift(1).fillna(False)
    two_red = red & red.shift(1).fillna(False)
    # a red run ended recently: a red HA candle in any of bars i-2..i-11,
    # so the entry still fires when the close needs a few bars to reclaim EMA50
    recent_red = red.shift(2).rolling(10, min_periods=1).max().fillna(0).astype(bool)
    recent_green = green.shift(2).rolling(10, min_periods=1).max().fillna(0).astype(bool)
    df["long_entry"] = (two_green & recent_red & (df["c"] > df["ema50"])).astype(bool)
    df["short_entry"] = (two_red & recent_green & (df["c"] < df["ema50"])).astype(bool)
    df["long_exit"] = red.astype(bool)
    df["short_exit"] = green.astype(bool)
    return df
