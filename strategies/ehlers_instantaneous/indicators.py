"""John Ehlers Instantaneous Trendline (Cycle Analytics for Traders).

With alpha = 0.07 the trendline is the recursive filter:

    IT[i] = (alpha - alpha^2/4) * P[i]
          + 0.5 * alpha^2 * P[i-1]
          - (alpha - 0.75 * alpha^2) * P[i-2]
          + 2 * (1 - alpha) * IT[i-1]
          - (1 - alpha)^2 * IT[i-2]

where P is close. The coefficients sum to 1 (price terms sum to
alpha^2, recursion terms sum to 1 - alpha^2), so a flat price
series reproduces itself exactly — the filter has zero gain error
at DC and behaves as a low-lag smoother: it tracks price closely
in trends and lags far less than an SMA/EMA of comparable
smoothness, which is the whole point of trading the price/IT
cross rather than a price/SMA cross.

Seeding: IT[0] = P[0], IT[1] = P[1] (seeded with price, per the
spec). The recursion is strictly causal — IT[i] reads only
P[..i] and IT[..i-1] — so there is no lookahead.

Columns:

    it  -- Instantaneous Trendline (alpha = 0.07)
    atr -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

ALPHA = 0.07  # Ehlers' published Instantaneous Trendline alpha


def instantaneous_trendline(price: pd.Series,
                            alpha: float = ALPHA) -> pd.Series:
    """Ehlers Instantaneous Trendline, seeded with price."""
    p = np.asarray(price, dtype=float)
    n = len(p)
    it = np.empty(n, dtype=float)
    if n == 0:
        return pd.Series(it, index=price.index, name="it")
    it[0] = p[0]
    if n > 1:
        it[1] = p[1]
    a = alpha
    c0 = a - a * a / 4.0
    c1 = 0.5 * a * a
    c2 = -(a - 0.75 * a * a)
    d1 = 2.0 * (1.0 - a)
    d2 = -(1.0 - a) ** 2
    for i in range(2, n):
        it[i] = (c0 * p[i] + c1 * p[i - 1] + c2 * p[i - 2]
                 + d1 * it[i - 1] + d2 * it[i - 2])
    return pd.Series(it, index=price.index, name="it")


def add_indicators(df: pd.DataFrame, alpha: float = ALPHA) -> pd.DataFrame:
    df = df.copy()
    df["it"] = instantaneous_trendline(df["c"], alpha)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
