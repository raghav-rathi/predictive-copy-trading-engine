"""Three white soldiers / three black crows signals.

Long: three white soldiers complete on bar i after a downtrend (close
below SMA(50) for each of the 5 bars before the pattern) -> enter on
the close of the 3rd candle. Short: three black crows complete after
an uptrend -> enter. Exit: a long exits on a close below the 1st
soldier's open; a short exits on a close above the 1st crow's open.
The pattern bar's open is tracked forward (the level stays armed
until a newer pattern refreshes it). Signals on bar i use only data
through bar i's close.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    df["long_entry"] = df["tws_bullish"].astype(bool)
    df["short_entry"] = df["tws_bearish"].astype(bool)
    # Open of the 1st soldier / 1st crow: the pattern completes on
    # bar i, so the 1st candle is bar i-2.
    s1_open = df["o"].shift(2).where(df["tws_bullish"]).ffill()
    c1_open = df["o"].shift(2).where(df["tws_bearish"]).ffill()
    df["long_exit"] = (c < s1_open).fillna(False).astype(bool)
    df["short_exit"] = (c > c1_open).fillna(False).astype(bool)
    return df
