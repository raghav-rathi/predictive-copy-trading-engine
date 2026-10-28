"""Smoothed Heikin-Ashi trend.

Standard Heikin-Ashi candles first:
    ha_close = (o + h + l + c) / 4
    ha_open[0] = (o[0] + c[0]) / 2
    ha_open[i] = (ha_open[i-1] + ha_close[i-1]) / 2
    ha_high = max(h, ha_open, ha_close)
    ha_low  = min(l, ha_open, ha_close)

Then the smoothing step that defines this variant: ha_open and
ha_close are each passed through EMA(5). Smoothing strips the
single-bar noise that makes raw Heikin-Ashi flip on doji-like bars,
at the cost of a few bars of lag — the trade-off this strategy
is explicitly testing.

Columns:
    ha_open, ha_close, ha_high, ha_low -- raw Heikin-Ashi candles
    ha_open_smooth, ha_close_smooth -- EMA(5) of ha_open / ha_close
    atr -- Wilder ATR(14) for the risk layer

Causal: ha_open[i] reads only ha values through bar i-1 and the
current bar's OHLC; the EMAs read bars <= i only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

SMOOTH = 5


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o = df["o"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)

    ha_close = (o + h + l + c) / 4.0
    ha_open = np.empty(n, dtype=float)
    if n:
        ha_open[0] = (o[0] + c[0]) / 2.0
        for i in range(1, n):
            ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0
    ha_high = np.maximum(np.maximum(h, ha_open), ha_close)
    ha_low = np.minimum(np.minimum(l, ha_open), ha_close)

    df["ha_open"] = ha_open
    df["ha_close"] = ha_close
    df["ha_high"] = ha_high
    df["ha_low"] = ha_low
    df["ha_open_smooth"] = B.ema(pd.Series(ha_open, index=df.index), SMOOTH)
    df["ha_close_smooth"] = B.ema(pd.Series(ha_close, index=df.index), SMOOTH)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
