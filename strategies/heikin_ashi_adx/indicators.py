"""Heikin Ashi trend + Wilder ADX filter indicators.

Heikin Ashi (Dan Valcu, 2004; formulas per the Heikin-Ashi
chart Wikipedia page): ha_close = (o + h + l + c) / 4;
ha_open = (prev ha_open + prev ha_close) / 2, seeded with
the first real open; ha_high = max(h, ha_open, ha_close);
ha_low = min(l, ha_open, ha_close). ADX(14) via base.adx
gives the ADX line plus the +DI / -DI lines used as the
trend-direction filter.

Columns:
    ha_open, ha_high, ha_low, ha_close -- Heikin Ashi candles
    adx, plus_di, minus_di             -- Wilder ADX(14) + DI lines
    atr14                              -- ATR(14), diagnostic

No lookahead: the HA recursion and Wilder smoothing use data
through bar i only. Stops are computed on REAL prices by the
risk layer, never on HA values.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ADX_N = 14


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


def add_indicators(
    df: pd.DataFrame,
    adx_n: int = ADX_N,
) -> pd.DataFrame:
    df = df.copy()
    ha_open, ha_high, ha_low, ha_close = heikin_ashi(df["o"], df["h"], df["l"], df["c"])
    df["ha_open"] = ha_open
    df["ha_high"] = ha_high
    df["ha_low"] = ha_low
    df["ha_close"] = ha_close
    a = B.adx(df["h"], df["l"], df["c"], adx_n)
    df["adx"] = a["adx"]
    df["plus_di"] = a["plus_di"]
    df["minus_di"] = a["minus_di"]
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
