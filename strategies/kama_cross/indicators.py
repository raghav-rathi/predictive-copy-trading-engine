"""Kaufman Adaptive Moving Average (KAMA) indicators.

Perry Kaufman, "Smarter Trading" (1995). Two KAMAs with the same
fast/slow smoothing constants but different efficiency-ratio windows:

    ER_t  = |C_t - C_{t-n}| / sum_{i=1..n} |C_{t-i+1} - C_{t-i}|
    SC_t  = (ER_t * (2/3 - 2/31) + 2/31)^2
    KAMA_t = KAMA_{t-1} + SC_t * (C_t - KAMA_{t-1})

with fast SC = 2/(2+1) = 2/3 and slow SC = 2/(30+1) = 2/31.
Seeded at the first close (KAMA_0 = C_0). For bars i < n the
efficiency ratio uses the available window (direction over the
bars seen so far divided by the sum of the absolute moves seen
so far); a flat stretch gives ER = 0 and the slow smoothing
constant, so KAMA holds still. The recursion is an explicit
causal loop: the value on bar j uses closes through bar j only.

Columns:
    kama_fast -- KAMA(ER 10, fast 2, slow 30)
    kama_slow -- KAMA(ER 20, fast 2, slow 30)
    atr14     -- ATR(14), diagnostic (the harness computes its own)
"""

import numpy as np
import pandas as pd

from strategies import base as B

ER_FAST = 10
ER_SLOW = 20
FAST_N = 2
SLOW_N = 30


def kama(c, er_period: int, fast_n: int = FAST_N, slow_n: int = SLOW_N) -> pd.Series:
    """Kaufman's adaptive moving average, exact recursion, seeded at C_0."""
    c_v = np.asarray(c, dtype=float)
    m = len(c_v)
    out = np.full(m, np.nan)
    if m == 0:
        return pd.Series(out, index=c.index)
    fast_sc = 2.0 / (fast_n + 1)
    slow_sc = 2.0 / (slow_n + 1)
    out[0] = c_v[0]
    abs_diff = np.abs(np.diff(c_v))  # abs_diff[i-1] = |C_i - C_{i-1}|
    for i in range(1, m):
        w = min(i, er_period)
        direction = abs(c_v[i] - c_v[i - w])
        volatility = abs_diff[i - w : i].sum()
        er = direction / volatility if volatility > 0 else 0.0
        sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
        out[i] = out[i - 1] + sc * (c_v[i] - out[i - 1])
    return pd.Series(out, index=c.index)


def add_indicators(
    df: pd.DataFrame,
    er_fast: int = ER_FAST,
    er_slow: int = ER_SLOW,
    fast_n: int = FAST_N,
    slow_n: int = SLOW_N,
) -> pd.DataFrame:
    df = df.copy()
    df["kama_fast"] = kama(df["c"], er_fast, fast_n, slow_n)
    df["kama_slow"] = kama(df["c"], er_slow, fast_n, slow_n)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
