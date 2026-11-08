"""Rising/falling three methods indicators.

Rising three methods: in an uptrend (close above SMA(50) on the
entry bar), bar 1 is a long bullish candle (body >= 1.0 x ATR(14)
measured at bar 1), bars 2-4 are small bearish candles (close <
open) each fully inside bar 1's range (high < bar 1 high, low >
bar 1 low), and bar 5 is a bullish candle closing above bar 1's
high. Falling three methods is the mirror image. rtm_bar1_high /
rtm_bar1_low hold bar 1's extremes on the pattern bar and are
forward-filled afterwards so the exit rule can reference them.
"""

import numpy as np
import pandas as pd

from strategies.base import atr, sma

INDICATOR_COLS = [
    "sma50",
    "atr14",
    "rtm_bullish",
    "rtm_bearish",
    "rtm_bar1_high",
    "rtm_bar1_low",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o = df["o"]
    h = df["h"]
    l = df["l"]
    c = df["c"]
    df["sma50"] = sma(c, 50)
    df["atr14"] = atr(h, l, c, 14)
    o1 = o.shift(4)
    h1 = h.shift(4)
    l1 = l.shift(4)
    c1 = c.shift(4)
    body1 = c1 - o1
    atr1 = df["atr14"].shift(4)
    # Bars 2-4 (shifts 3, 2, 1) inside bar 1's range.
    inside = (
        (h.shift(3) < h1) & (l.shift(3) > l1)
        & (h.shift(2) < h1) & (l.shift(2) > l1)
        & (h.shift(1) < h1) & (l.shift(1) > l1)
    )
    small_bearish = (c.shift(3) < o.shift(3)) & (c.shift(2) < o.shift(2)) & (c.shift(1) < o.shift(1))
    small_bullish = (c.shift(3) > o.shift(3)) & (c.shift(2) > o.shift(2)) & (c.shift(1) > o.shift(1))
    bullish = (
        (c > df["sma50"])
        & (body1 >= atr1)
        & small_bearish
        & inside
        & (c > o)
        & (c > h1)
    ).fillna(False)
    bearish = (
        (c < df["sma50"])
        & (-body1 >= atr1)
        & small_bullish
        & inside
        & (c < o)
        & (c < l1)
    ).fillna(False)
    df["rtm_bullish"] = bullish.astype(bool)
    df["rtm_bearish"] = bearish.astype(bool)
    either = bullish | bearish
    df["rtm_bar1_high"] = pd.Series(np.where(either, h1, np.nan), index=df.index).ffill()
    df["rtm_bar1_low"] = pd.Series(np.where(either, l1, np.nan), index=df.index).ffill()
    return df
