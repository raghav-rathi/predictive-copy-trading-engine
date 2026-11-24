"""Ehlers SuperSmoother indicators.

John F. Ehlers' SuperSmoother is a 2-pole Butterworth low-pass
filter applied to price. Unlike an EMA, which lags and overshoots
on sharp moves, the SuperSmoother has (near-)zero lag at low
frequencies and a maximally flat passband, so a fast/slow pair of
SuperSmoothers tracks trend turns with less whipsaw than a
moving-average crossover of the same periods.

For a filter period n, with P = close:

    a1 = exp(-1.414 * pi / n)
    b1 = 2 * a1 * cos(1.414 * pi / n)
    c2 = b1
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    filt[i] = c1 * (P[i] + P[i-1]) / 2 + c2 * filt[i-1] + c3 * filt[i-2]

The recursion is an explicit loop (~5,900 bars is cheap). The first
two filter values are seeded with the price itself so the series
has no NaN head and no lookahead: the value on bar i uses closes
through bar i only.

Columns:
    ss_fast  -- SuperSmoother(10) of close
    ss_slow  -- SuperSmoother(30) of close

Source: John F. Ehlers, "Cybernetic Analysis for Stocks and
Futures" (2004).
"""

import numpy as np
import pandas as pd

FAST_N = 10  # shipped default
SLOW_N = 30  # shipped default


def supersmoother(c: pd.Series, n: int) -> pd.Series:
    """Ehlers 2-pole SuperSmoother of a price series (explicit loop)."""
    import math

    p = c.to_numpy(dtype=float)
    m = len(p)
    out = np.empty(m, dtype=float)
    if m == 0:
        return pd.Series(out, index=c.index)
    a1 = math.exp(-1.414 * math.pi / n)
    b1 = 2.0 * a1 * math.cos(1.414 * math.pi / n)
    c2 = b1
    c3 = -a1 * a1
    c1 = 1.0 - c2 - c3
    out[0] = p[0]
    if m > 1:
        out[1] = p[1]
    for i in range(2, m):
        out[i] = (
            c1 * (p[i] + p[i - 1]) / 2.0 + c2 * out[i - 1] + c3 * out[i - 2]
        )
    return pd.Series(out, index=c.index)


def add_indicators(
    df: pd.DataFrame,
    fast_n: int = FAST_N,
    slow_n: int = SLOW_N,
) -> pd.DataFrame:
    df = df.copy()
    df["ss_fast"] = supersmoother(df["c"], fast_n)
    df["ss_slow"] = supersmoother(df["c"], slow_n)
    return df
