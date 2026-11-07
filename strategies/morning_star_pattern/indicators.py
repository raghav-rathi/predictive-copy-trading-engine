"""Morning/Evening Star indicators (Steve Nison candlesticks).

Morning star (3 candles, completes on bar i):
  candle1 (i-2): long red body, body >= 0.6x ATR(14)
  candle2 (i-1): small body, body <= 0.3x candle1's body
  candle3 (i):   long green body closing beyond the midpoint of
                 candle1's body
  trend filter: close[i] below SMA(50) (downtrend)
Evening star is the mirror image, with close[i] above SMA(50).
No gap requirement: crypto trades 24/7, so gaps are not part of the
pattern. All quantities use data through bar i's close only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

INDICATOR_COLS = [
    "atr14",
    "sma50",
    "ms_morning",
    "ms_evening",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o = df["o"]
    c = df["c"]
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    df["sma50"] = B.sma(df["c"], 50)
    body = (c - o).abs()
    body1 = body.shift(2)
    body2 = body.shift(1)
    body3 = body
    atr = df["atr14"]
    o1, c1 = o.shift(2), c.shift(2)
    o2, c2 = o.shift(1), c.shift(1)
    o3, c3 = o, c
    mid1 = (o1 + c1) / 2.0
    morning = (
        (c1 < o1)                       # candle1 red
        & (body1 >= 0.6 * atr)          # candle1 long body
        & (body2 <= 0.3 * body1)        # candle2 small body
        & (c3 > o3)                     # candle3 green
        & (c3 > mid1)                   # candle3 closes beyond midpoint
        & (c < df["sma50"])             # downtrend
    )
    evening = (
        (c1 > o1)                       # candle1 green
        & (body1 >= 0.6 * atr)          # candle1 long body
        & (body2 <= 0.3 * body1)        # candle2 small body
        & (c3 < o3)                     # candle3 red
        & (c3 < mid1)                   # candle3 closes beyond midpoint
        & (c > df["sma50"])             # uptrend
    )
    df["ms_morning"] = morning.fillna(False).astype(float)
    df["ms_evening"] = evening.fillna(False).astype(float)
    return df
