"""Wilder DMI/ADX indicators + self-contained Parabolic SAR.

+DI(14), -DI(14), ADX(14) use Wilder smoothing via strategies.base.adx (the
exact Wilder formulation). The Parabolic SAR (AF 0.02/0.2) is implemented here
as a local loop — deliberately NOT imported from strategies.parabolic_sar, so
this package stays a clean branch delta.

Classic SAR rules: SAR accelerates toward the extreme point (EP) by AF each
bar; in an uptrend SAR can never exceed the prior two bars' lows; a print
through SAR flips the trend, SAR resets to the prior EP, and AF resets.
"""

import numpy as np
import pandas as pd

from strategies import base as B

DI_LEN = 14
ADX_MIN = 25.0
SAR_START = 0.02
SAR_STEP = 0.02
SAR_MAX = 0.20


def parabolic_sar(h, l, c, start=SAR_START, step=SAR_STEP, max_af=SAR_MAX):
    """Classic Parabolic SAR. Returns (sar, trend) with trend +1/-1."""
    h = np.asarray(h, dtype=float)
    l = np.asarray(l, dtype=float)
    c = np.asarray(c, dtype=float)
    n = len(c)
    sar = np.full(n, np.nan)
    trend = np.zeros(n, dtype=int)
    if n < 2:
        return sar, trend
    up = bool(c[1] >= c[0])
    trend[0] = 1 if up else -1
    sar_p = l[0] if up else h[0]
    ep = max(h[0], h[1]) if up else min(l[0], l[1])
    af = start
    sar[0] = sar_p
    for i in range(1, n):
        s = sar_p + af * (ep - sar_p)
        if up:
            prev_lows = l[i - 1] if i < 2 else min(l[i - 1], l[i - 2])
            s = min(s, prev_lows)
            if l[i] < s:
                up = False
                sar[i] = ep
                trend[i] = -1
                ep = l[i]
                af = start
                sar_p = ep
                continue
            if h[i] > ep:
                ep = h[i]
                af = min(af + step, max_af)
            sar[i] = s
            trend[i] = 1
            sar_p = s
        else:
            prev_highs = h[i - 1] if i < 2 else max(h[i - 1], h[i - 2])
            s = max(s, prev_highs)
            if h[i] > s:
                up = True
                sar[i] = ep
                trend[i] = 1
                ep = h[i]
                af = start
                sar_p = ep
                continue
            if l[i] < ep:
                ep = l[i]
                af = min(af + step, max_af)
            sar[i] = s
            trend[i] = -1
            sar_p = s
    return sar, trend


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = B.adx(df["h"], df["l"], df["c"], DI_LEN)
    df["adx"] = d["adx"]
    df["plus_di"] = d["plus_di"]
    df["minus_di"] = d["minus_di"]
    df["adx_prev"] = df["adx"].shift(1)
    sar, trend = parabolic_sar(df["h"], df["l"], df["c"])
    df["sar"] = sar
    df["sar_trend"] = trend
    df["sar_trend_prev"] = pd.Series(trend, index=df.index).shift(1)
    return df
