"""Heikin Ashi + EMA trend filter indicators.

Heikin Ashi candles:
    HA close = (open + high + low + close) / 4
    HA open  = (previous HA open + previous HA close) / 2
    (seeded on bar 0 with (open + close) / 2)
HA high / low are not needed by the signals and are not published.

Trend filter: EMA(9), EMA(21), EMA(50) of close (standard
exponential averages, causal).

Columns:
    ha_open / ha_close -- Heikin Ashi open/close
    ema_fast (9) / ema_mid (21) / ema_slow (50)
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only. HA open is recursive forward only; EMAs are trailing.
"""

import numpy as np
import pandas as pd

from strategies import base as B

EMA_FAST = 9
EMA_MID = 21
EMA_SLOW = 50
ATR_N = 14


def add_indicators(df: pd.DataFrame, ema_fast: int = EMA_FAST,
                   ema_mid: int = EMA_MID, ema_slow: int = EMA_SLOW,
                   atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    o = df["o"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)

    ha_close = (o + h + l + c) / 4.0
    ha_open = np.full(n, np.nan)
    if n:
        ha_open[0] = (o[0] + c[0]) / 2.0
        for i in range(1, n):
            ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0
    df["ha_open"] = ha_open
    df["ha_close"] = ha_close
    df["ema_fast"] = B.ema(df["c"], ema_fast)
    df["ema_mid"] = B.ema(df["c"], ema_mid)
    df["ema_slow"] = B.ema(df["c"], ema_slow)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    return df
