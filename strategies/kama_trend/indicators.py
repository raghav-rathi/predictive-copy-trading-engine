"""KAMA indicators (Perry Kaufman, Kaufman Adaptive Moving Average).

Efficiency Ratio (n=10):
    ER[i] = |c[i] - c[i-n]| / sum(|c[j] - c[j-1]| for j in i-n+1..i)
    ER = 1 on a straight-line trend, -> 0 in sideways chop.
    A flat market (zero denominator) is assigned ER = 0.

Scaled smoothing constant (fast=2, slow=30):
    fastSC = 2/(2+1) = 0.6667, slowSC = 2/(30+1) = 0.06452
    SC[i] = (ER[i]*(fastSC - slowSC) + slowSC)^2

KAMA recursion (causal, no lookahead):
    kama[i] = kama[i-1] + SC[i]*(c[i] - kama[i-1]),
seeded at the first valid ER index with SMA(c, n).
"""

import numpy as np
import pandas as pd

from strategies import base as B

N = 10
FAST_N = 2
SLOW_N = 30
ER_MIN = 0.3  # efficiency filter threshold for entries (signals.py)
ATR_N = 14

FAST_SC = 2.0 / (FAST_N + 1)  # 0.6667
SLOW_SC = 2.0 / (SLOW_N + 1)  # 0.06452


def efficiency_ratio(c: pd.Series, n: int = N) -> pd.Series:
    num = (c - c.shift(n)).abs()
    den = c.diff().abs().rolling(n, min_periods=n).sum()
    er = num / den
    # flat market: 0/0 -> zero efficiency (keeps NaN where not enough history)
    er = er.where(den != 0, 0.0)
    return er.clip(0.0, 1.0)


def smoothing_constant(er: pd.Series) -> pd.Series:
    return (er * (FAST_SC - SLOW_SC) + SLOW_SC) ** 2


def kama(c: pd.Series, sc: pd.Series, n: int = N) -> pd.Series:
    """Causal KAMA recursion. Reads module N/SC at call time; positional
    float recursion, so end-truncation of the frame changes nothing at the
    retained bars (seed index is positional within the passed frame)."""
    c_v = c.to_numpy(dtype=float)
    sc_v = sc.to_numpy(dtype=float)
    out = np.full(len(c_v), np.nan)
    valid = np.where(~np.isnan(sc_v))[0]
    if len(valid) == 0:
        return pd.Series(out, index=c.index)
    j0 = int(valid[0])
    # seed with SMA(c, n) at the first valid index
    window = c_v[max(0, j0 - n + 1) : j0 + 1]
    out[j0] = float(np.mean(window)) if not np.isnan(window).any() else c_v[j0]
    prev = out[j0]
    for i in range(j0 + 1, len(c_v)):
        if np.isnan(c_v[i]):
            out[i] = prev
            continue
        s = sc_v[i] if not np.isnan(sc_v[i]) else 0.0
        prev = prev + s * (c_v[i] - prev)
        out[i] = prev
    return pd.Series(out, index=c.index)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["er"] = efficiency_ratio(df["c"], N)
    df["sc"] = smoothing_constant(df["er"])
    df["kama"] = kama(df["c"], df["sc"], N)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
