"""Adaptive RSI indicators (Kaufman efficiency-ratio smoothing).

The efficiency ratio ER(10) = |close - close[10]| / sum |daily
changes| over 10 bars: 1 in a clean trend, near 0 in chop. The
smoothing constant SC = (ER * (2/3 - 2/31) + 2/31)^2 adapts the
RSI(14) average: fast when ER is high, slow when it is low. The
result is an RSI that reacts quickly in trends and refuses to
chase chop.

Columns:
    rsi14, arsi, atr
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsi_v = B.rsi(df["c"], 14)
    c = df["c"]
    er = (c - c.shift(10)).abs() / c.diff().abs().rolling(10).sum().replace(0, np.nan)
    sc = (er * (2.0 / 3 - 2.0 / 31) + 2.0 / 31) ** 2
    r = rsi_v.to_numpy()
    sc_v = sc.to_numpy()
    n = len(df)
    ama = np.full(n, np.nan)
    valid = np.where(~np.isnan(r) & ~np.isnan(sc_v))[0]
    if len(valid):
        j = int(valid[0])
        ama[j] = r[j]
        for i in range(j + 1, n):
            if np.isnan(r[i]) or np.isnan(sc_v[i]):
                ama[i] = ama[i - 1]
            else:
                ama[i] = ama[i - 1] + sc_v[i] * (r[i] - ama[i - 1])
    df["rsi14"] = rsi_v
    df["arsi"] = ama
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
