"""Heikin Ashi trend indicators (Dan Valcu, 2004).

HA close = (o + h + l + c) / 4
HA open  = (prev HA open + prev HA close) / 2   (seeded with the first real open)
HA high  = max(h, HA open, HA close)
HA low   = min(l, HA open, HA close)

Stops are computed on REAL prices by the risk layer, never on HA values.
"""

import numpy as np
import pandas as pd

from strategies import base as B

EMA_PERIOD = 50

INDICATOR_COLS = ["ha_open", "ha_high", "ha_low", "ha_close", "ema50"]


def heikin_ashi(o, h, l, c):
    """Return (ha_open, ha_high, ha_low, ha_close) as numpy arrays."""
    o_v = np.asarray(o, dtype=float)
    h_v = np.asarray(h, dtype=float)
    l_v = np.asarray(l, dtype=float)
    c_v = np.asarray(c, dtype=float)
    n = len(c_v)
    ha_close = (o_v + h_v + l_v + c_v) / 4.0
    ha_open = np.empty(n)
    ha_open[0] = o_v[0]
    for i in range(1, n):
        ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0
    ha_high = np.maximum(np.maximum(h_v, ha_open), ha_close)
    ha_low = np.minimum(np.minimum(l_v, ha_open), ha_close)
    return ha_open, ha_high, ha_low, ha_close


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ha_open, ha_high, ha_low, ha_close = heikin_ashi(df["o"], df["h"], df["l"], df["c"])
    df["ha_open"] = ha_open
    df["ha_high"] = ha_high
    df["ha_low"] = ha_low
    df["ha_close"] = ha_close
    df["ema50"] = B.ema(df["c"], EMA_PERIOD)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
