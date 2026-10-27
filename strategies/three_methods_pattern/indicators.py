"""Nison rising/falling three methods, 5-bar pattern.

Rising: bar i-4 is a strong up candle (body >= 60% of range); bars
i-3..i-1 are small (body < 50% of the first body) and contained
inside bar i-4's high-low range; bar i is a strong up candle
closing above bar i-4's close. Falling is the mirror. The middle
candles need not drift monotonically — containment is the rule.
Columns: methods_dir (+1/-1/0), atr.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def _methods(o, h, l, c):
    n = len(c)
    out = np.zeros(n, dtype=int)
    body = np.abs(c - o)
    rng = h - l
    for i in range(4, n):
        j = i - 4
        if body[j] < 0.6 * rng[j] or rng[j] <= 0:
            continue
        mid_ok = True
        for k in range(j + 1, i):
            if body[k] >= 0.5 * body[j] or h[k] > h[j] or l[k] < l[j]:
                mid_ok = False
                break
        if not mid_ok:
            continue
        if c[j] > o[j] and c[i] > o[i] and body[i] >= 0.6 * rng[i] and c[i] > c[j]:
            out[i] = 1
        elif c[j] < o[j] and c[i] < o[i] and body[i] >= 0.6 * rng[i] and c[i] < c[j]:
            out[i] = -1
    return out


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["methods_dir"] = _methods(
        df["o"].to_numpy(dtype=float),
        df["h"].to_numpy(dtype=float),
        df["l"].to_numpy(dtype=float),
        df["c"].to_numpy(dtype=float),
    )
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
