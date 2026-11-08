"""RSI pullback in trend signals.

Long trend: SMA50 > SMA200. A pullback bar is one whose low touches
or dips to the 50 SMA (low <= SMA50) while RSI(14) is in 40-55.
Entry on the first bar within 5 bars after a pullback bar whose close
is back above SMA50 (i.e. a close crossing back up through SMA50).
Exit: RSI(14) > 70 or close below SMA200. Short mirror: SMA50 <
SMA200, high >= SMA50 with RSI(14) in 45-60, entry on a close
crossing back below SMA50 within 5 bars; exit RSI(14) < 30 or close
above SMA200. Pullback bars and the cross are evaluated on closes
through bar i only, so signals on bar i use no future data.
"""

import numpy as np
import pandas as pd

PULLBACK_WINDOW = 5


def _armed_within(pullback: pd.Series, window: int) -> pd.Series:
    """True on bars within `window` bars after a pullback bar."""
    return (
        pullback.fillna(False)
        .shift(1)
        .rolling(window, min_periods=1)
        .max()
        .fillna(False)
        .astype(bool)
    )


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    l = df["l"]
    h = df["h"]
    sma50 = df["sma50"]
    sma200 = df["sma200"]
    rsi14 = df["rsi14"]
    trend_up = (sma50 > sma200).fillna(False)
    trend_down = (sma50 < sma200).fillna(False)
    pull_long = (
        (l <= sma50) & (rsi14 >= 40) & (rsi14 <= 55) & trend_up
    ).fillna(False)
    pull_short = (
        (h >= sma50) & (rsi14 >= 45) & (rsi14 <= 60) & trend_down
    ).fillna(False)
    cross_up = ((c > sma50) & (c.shift(1) <= sma50.shift(1))).fillna(False)
    cross_down = ((c < sma50) & (c.shift(1) >= sma50.shift(1))).fillna(False)
    df["long_entry"] = (_armed_within(pull_long, PULLBACK_WINDOW) & cross_up).astype(bool)
    df["short_entry"] = (_armed_within(pull_short, PULLBACK_WINDOW) & cross_down).astype(bool)
    df["long_exit"] = ((rsi14 > 70) | (c < sma200)).fillna(False).astype(bool)
    df["short_exit"] = ((rsi14 < 30) | (c > sma200)).fillna(False).astype(bool)
    return df
