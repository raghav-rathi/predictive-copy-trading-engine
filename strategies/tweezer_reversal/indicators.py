"""Tweezer top/bottom reversal indicators.

Tweezer bottom: after a downtrend (close below SMA(50) for the five
bars immediately preceding bar 1 of the pattern), two consecutive
bars whose lows are equal within 0.1 x ATR(14), bar 1 bearish and
bar 2 bullish closing above bar 1's midpoint. Tweezer top is the
mirror image. twz_low / twz_high hold the tweezer extremes (min of
the two lows / max of the two highs) on the pattern bar and are
forward-filled afterwards so the exit rule can reference them.
"""

import numpy as np
import pandas as pd

from strategies.base import atr, sma

TOL_ATR_MULT = 0.1
TREND_BARS = 5

INDICATOR_COLS = [
    "sma50",
    "atr14",
    "twz_bottom",
    "twz_top",
    "twz_low",
    "twz_high",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o = df["o"]
    h = df["h"]
    l = df["l"]
    c = df["c"]
    df["sma50"] = sma(c, 50)
    df["atr14"] = atr(h, l, c, 14)
    # Trend over the five bars immediately preceding bar 1 of the
    # pattern (indices i-6..i-2 for a pattern completing on bar i).
    below = (c < df["sma50"]).fillna(False)
    above = (c > df["sma50"]).fillna(False)
    downtrend = (below.rolling(TREND_BARS, min_periods=TREND_BARS).sum().shift(2) >= TREND_BARS).fillna(False)
    uptrend = (above.rolling(TREND_BARS, min_periods=TREND_BARS).sum().shift(2) >= TREND_BARS).fillna(False)
    o1 = o.shift(1)
    c1 = c.shift(1)
    h1 = h.shift(1)
    l1 = l.shift(1)
    tol = TOL_ATR_MULT * df["atr14"]
    mid1 = (o1 + c1) / 2.0
    bottom = (
        downtrend
        & ((l - l1).abs() <= tol)
        & (c1 < o1)
        & (c > o)
        & (c > mid1)
    ).fillna(False)
    top = (
        uptrend
        & ((h - h1).abs() <= tol)
        & (c1 > o1)
        & (c < o)
        & (c < mid1)
    ).fillna(False)
    df["twz_bottom"] = bottom.astype(bool)
    df["twz_top"] = top.astype(bool)
    df["twz_low"] = pd.Series(np.where(bottom, np.minimum(l, l1), np.nan), index=df.index).ffill()
    df["twz_high"] = pd.Series(np.where(top, np.maximum(h, h1), np.nan), index=df.index).ffill()
    return df
