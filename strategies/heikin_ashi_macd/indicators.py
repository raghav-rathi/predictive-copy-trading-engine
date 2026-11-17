"""Heikin Ashi + MACD momentum filter indicators.

Heikin Ashi candles (per the TradingView source):

    HA-close = (o + h + l + c) / 4
    HA-open  = (prev HA-open + prev HA-close) / 2
             (seeded on the first bar as (o + c) / 2)
    HA-high  = max(h, HA-open, HA-close)
    HA-low   = min(l, HA-open, HA-close)

MACD(12, 26, 9) is computed on the HA close.

Columns:

    ha_o, ha_h, ha_l, ha_c  -- Heikin Ashi candles
    macd, macd_signal, macd_hist -- MACD(12, 26, 9) on HA close
    atr                     -- Wilder ATR(14) on the raw candles,
                               for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

INDICATOR_COLS = ["ha_o", "ha_h", "ha_l", "ha_c",
                  "macd", "macd_signal", "macd_hist", "atr"]


def heikin_ashi(o, h, l, c):
    """Return (ha_o, ha_h, ha_l, ha_c) as numpy arrays.

    HA-open is recursive, so this is an explicit loop over the bars.
    The first bar is seeded with HA-open = (o + c) / 2.
    """
    o = np.asarray(o, dtype=float)
    h = np.asarray(h, dtype=float)
    l = np.asarray(l, dtype=float)
    c = np.asarray(c, dtype=float)
    n = len(c)
    ha_c = (o + h + l + c) / 4.0
    ha_o = np.empty(n)
    ha_h = np.empty(n)
    ha_l = np.empty(n)
    prev_o = (o[0] + c[0]) / 2.0 if n else 0.0
    for i in range(n):
        cur_o = prev_o if i == 0 else (prev_o + ha_c[i - 1]) / 2.0
        ha_o[i] = cur_o
        ha_h[i] = max(h[i], cur_o, ha_c[i])
        ha_l[i] = min(l[i], cur_o, ha_c[i])
        prev_o = cur_o
    return ha_o, ha_h, ha_l, ha_c


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ha_o, ha_h, ha_l, ha_c = heikin_ashi(df["o"], df["h"], df["l"], df["c"])
    df["ha_o"] = ha_o
    df["ha_h"] = ha_h
    df["ha_l"] = ha_l
    df["ha_c"] = ha_c
    macd = B.macd(pd.Series(ha_c, index=df.index),
                  fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
    df["macd"] = macd["macd"]
    df["macd_signal"] = macd["macd_signal"]
    df["macd_hist"] = macd["macd_hist"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
