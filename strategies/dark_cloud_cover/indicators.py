"""Dark cloud cover / piercing pattern indicators.

dcc_bearish is True on the bar where a dark cloud cover completes:
after an uptrend (bar 1 closes above SMA(50)), bar 1 is bullish with
a body of at least 0.6 x its range, and bar 2 opens above bar 1's high
and closes below bar 1's midpoint. dcc_bullish is the mirror
(piercing pattern after a downtrend). dcc_bar2_high / dcc_bar2_low
carry bar 2's high / low on the pattern bar (NaN elsewhere); the
signals layer forward-fills them for the exit check. sma50 is the
50-bar simple moving average of close. All quantities use only data
through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies.base import sma

SMA_BARS = 50
MIN_BODY_FRAC = 0.6

INDICATOR_COLS = [
    "dcc_sma50",
    "dcc_bearish",
    "dcc_bullish",
    "dcc_bar2_high",
    "dcc_bar2_low",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o = df["o"]
    h = df["h"]
    l = df["l"]
    c = df["c"]
    df["dcc_sma50"] = sma(c, SMA_BARS)
    o1 = o.shift(1)
    h1 = h.shift(1)
    l1 = l.shift(1)
    c1 = c.shift(1)
    sma1 = df["dcc_sma50"].shift(1)
    rng1 = h1 - l1
    mid1 = (o1 + c1) / 2.0
    bar1_bull = (c1 > o1) & ((c1 - o1) >= MIN_BODY_FRAC * rng1)
    bar1_bear = (c1 < o1) & ((o1 - c1) >= MIN_BODY_FRAC * rng1)
    # Dark cloud cover: uptrend, bullish bar 1, bar 2 gaps above bar
    # 1's high and closes below bar 1's midpoint.
    dcc_bearish = (
        (c1 > sma1) & bar1_bull & (o > h1) & (c < mid1)
    ).fillna(False)
    # Piercing pattern: downtrend, bearish bar 1, bar 2 gaps below
    # bar 1's low and closes above bar 1's midpoint.
    dcc_bullish = (
        (c1 < sma1) & bar1_bear & (o < l1) & (c > mid1)
    ).fillna(False)
    df["dcc_bearish"] = dcc_bearish.astype(bool)
    df["dcc_bullish"] = dcc_bullish.astype(bool)
    df["dcc_bar2_high"] = h.where(dcc_bearish)
    df["dcc_bar2_low"] = l.where(dcc_bullish)
    return df
