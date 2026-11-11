"""John Ehlers' RSI on SuperSmoother-filtered closes.

Ehlers, "Cycle Analytics for Traders" (2013): run the classic Wilder
RSI on a SuperSmoother-filtered close series instead of raw closes,
so the oscillator reacts to the cycle rather than to bar-to-bar noise.
The SuperSmoother is the standard 2-pole recursion (same coefficients
as strategies/ehlers_supersmoother, period 10 here):

    a1 = exp(-1.414 * pi / 10)
    b1 = 2 * a1 * cos(1.414 * 180 / 10)      # argument in degrees
    c2 = b1; c3 = -a1^2; c1 = 1 - c2 - c3
    ss[i] = c1 * (close[i] + close[i-1]) / 2 + c2 * ss[i-1] + c3 * ss[i-2]

seeded with the price itself for the first two bars, then Wilder
RSI(14) on the smoothed series (shared strategies.base.rsi).

All computation is causal: every value on bar i uses only data through
bar i's close. Distinct from adaptive_rsi, which is Kaufman-AMA based.
"""

import math

import numpy as np
import pandas as pd

from strategies.base import rsi

SS_PERIOD = 10
RSI_PERIOD = 14

INDICATOR_COLS = ["ss_close", "rsi_ss"]


def supersmoother_coefs(period: int = SS_PERIOD) -> dict:
    """Ehlers SuperSmoother coefficients for a cutoff ``period``."""
    a1 = math.exp(-1.414 * math.pi / period)
    b1 = 2 * a1 * math.cos(math.radians(1.414 * 180 / period))
    c2 = b1
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    return {"a1": a1, "b1": b1, "c1": c1, "c2": c2, "c3": c3}


def supersmoother(price: pd.Series, period: int = SS_PERIOD) -> pd.Series:
    """2-pole SuperSmoother recursion on a price series."""
    p = price.to_numpy(dtype=float)
    n = len(p)
    k = supersmoother_coefs(period)
    c1, c2, c3 = k["c1"], k["c2"], k["c3"]
    f = np.empty(n)
    if n > 0:
        f[0] = p[0]  # seed with price: no start-up blowup
    if n > 1:
        f[1] = p[1]
    for i in range(2, n):
        f[i] = c1 * (p[i] + p[i - 1]) / 2 + c2 * f[i - 1] + c3 * f[i - 2]
    return pd.Series(f, index=price.index)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ss = supersmoother(df["c"], SS_PERIOD)
    df["ss_close"] = ss
    df["rsi_ss"] = rsi(ss, RSI_PERIOD)
    return df
