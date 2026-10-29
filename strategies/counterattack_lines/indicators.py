"""Counterattack lines indicators (causal, no lookahead).

Two-candle reversal (Steve Nison, Japanese Candlestick Charting
Techniques ch. 6): after a trend, a long candle is followed by an
opposite-color candle that gaps against the trend at the open and
then fights all the way back to (nearly) the prior candle's close
— a stalemate that bridles the trend. The bullish version is a
weaker cousin of the piercing pattern: unlike piercing, the
second candle does NOT push well into the first candle's body,
it merely returns to the prior close.

    Bullish: bar i-1 long black, bar i white, bar i gaps down
        at the open (o[i] < c[i-1]), closes nearly at bar i-1's
        close (|c[i] - c[i-1]| <= 0.2 * ATR(14)), bodies of
        similar size (ratio within [2/3, 3/2]), and a 5-bar
        downtrend into bar i-1 (c[i-1] < c[i-6]).
    Bearish: mirror (long white, gap up at the open, close
        nearly at the prior close, similar size, 5-bar uptrend).

The pattern completes on bar i, so it uses only bars i-6..i.
The "nearly the same close" tolerance is in ATR units so it
scales across BTC/ETH/HYPE price levels.

Columns:
    counterattack_dir -- +1 on a bullish counterattack bar, -1
                         on a bearish counterattack bar, else 0
    atr               -- Wilder ATR(14) for the risk layer (and
                         the close-tolerance test)
"""

import numpy as np
import pandas as pd

from strategies import base as B

CLOSE_TOL_ATR = 0.2
BODY_RATIO_LO = 2.0 / 3.0
BODY_RATIO_HI = 3.0 / 2.0
TREND_BARS = 5


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    atr_s = B.atr(df["h"], df["l"], df["c"], 14)
    o = df["o"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    atr = atr_s.to_numpy(dtype=float)

    body = c - o
    direction = np.zeros(n, dtype=int)
    if n >= TREND_BARS + 2:
        i = np.arange(TREND_BARS + 1, n)  # second-candle index
        p = i - 1
        same_close = np.abs(c[i] - c[p]) <= CLOSE_TOL_ATR * atr[i]
        b1 = np.abs(body[p])
        b2 = np.abs(body[i])
        with np.errstate(invalid="ignore", divide="ignore"):
            ratio = np.where(b1 > 0, b2 / np.where(b1 > 0, b1, 1.0), np.nan)
        size_ok = (ratio >= BODY_RATIO_LO) & (ratio <= BODY_RATIO_HI)
        bull = (
            (c[p] < o[p]) & (c[i] > o[i])
            & (o[i] < c[p])
            & same_close & size_ok
            & (c[p] < c[p - TREND_BARS])
        )
        bear = (
            (c[p] > o[p]) & (c[i] < o[i])
            & (o[i] > c[p])
            & same_close & size_ok
            & (c[p] > c[p - TREND_BARS])
        )
        direction[i[bull]] = 1
        direction[i[bear]] = -1

    df["counterattack_dir"] = direction
    df["atr"] = atr_s
    return df
