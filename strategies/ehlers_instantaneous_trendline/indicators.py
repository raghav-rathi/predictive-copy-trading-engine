"""Ehlers Instantaneous Trendline indicators (John F. Ehlers,
Cybernetic Analysis for Stocks and Futures, 2004).

The Instantaneous Trendline (IT) is a near-zero-lag trend extractor:
a compact recursive filter that blends the last few closes with its
own prior outputs. With alpha = 0.07 (Ehlers' default):

    IT_t = (alpha - alpha^2/4) * c_t
         + 0.5 * alpha^2 * c_{t-1}
         - (alpha - 0.75 * alpha^2) * c_{t-2}
         + 2 * (1 - alpha) * IT_{t-1}
         - (1 - alpha)^2 * IT_{t-2}

The filter is seeded with the SMA of the closes available so far:
IT_0 = c_0 and IT_1 = mean(c_0, c_1). That seed is fully causal
(it uses only closes at or before the seeded bar) and the warmup
(60 bars) is far longer than the filter's settling time, so the seed
choice has no effect on traded bars.

Columns:

    it   -- the Instantaneous Trendline
    atr  -- Wilder ATR(14) for the risk layer

No lookahead: IT_t uses closes through bar t and its own prior
values only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ALPHA = 0.07

INDICATOR_COLS = ["it", "atr"]


def instantaneous_trendline(c, alpha: float = ALPHA) -> np.ndarray:
    c = np.asarray(c, dtype=float)
    n = len(c)
    it = np.empty(n, dtype=float)
    if n == 0:
        return it
    it[0] = c[0]
    if n == 1:
        return it
    it[1] = 0.5 * (c[0] + c[1])
    a = alpha
    w0 = a - a * a / 4.0
    w1 = 0.5 * a * a
    w2 = -(a - 0.75 * a * a)
    r1 = 2.0 * (1.0 - a)
    r2 = -(1.0 - a) * (1.0 - a)
    for i in range(2, n):
        it[i] = (w0 * c[i] + w1 * c[i - 1] + w2 * c[i - 2]
                 + r1 * it[i - 1] + r2 * it[i - 2])
    return it


def add_indicators(df: pd.DataFrame, alpha: float = ALPHA) -> pd.DataFrame:
    df = df.copy()
    df["it"] = instantaneous_trendline(df["c"].to_numpy(), alpha=alpha)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
