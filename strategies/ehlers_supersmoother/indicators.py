"""John Ehlers' SuperSmoother -- 2-pole recursive IIR low-pass filter.

Ehlers (Cybernetic Analysis for Stocks and Futures): a 2-pole filter
whose coefficients come from a DSP analog low-pass prototype, so it
delivers the smoothness of a ~20-bar average with roughly half the
lag of a simple moving average of the same period:

    a1 = exp(-1.414 * pi / period)
    b1 = 2 * a1 * cos(1.414 * 180 / period)      # argument in degrees!
    c2 = b1
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    filt[i] = c1 * (price[i] + price[i-1]) / 2 + c2 * filt[i-1] + c3 * filt[i-2]

Implemented on close with a numpy loop; the first two filter values
are seeded with price to avoid start-up blowup. Unity gain at DC
(c1 / (1 - c2 - c3) == 1), so the filter tracks the price level itself
and crosses of close vs the filter are meaningful trend-turn markers.

Columns:

    ss_filt    -- SuperSmoother(20) of close
    ss_rising  -- filter rising (filt > filt.shift(1))
    ss_falling -- filter falling (filt < filt.shift(1))
    atr        -- Wilder ATR(14) for the risk layer

No lookahead: filt[i] uses price through bar i only.
"""

import math

import numpy as np
import pandas as pd

from strategies import base as B

SS_PERIOD = 20  # shipped default


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


def add_indicators(df: pd.DataFrame, period: int = SS_PERIOD) -> pd.DataFrame:
    df = df.copy()
    f = supersmoother(df["c"], period)
    df["ss_filt"] = f
    df["ss_rising"] = f > f.shift(1)
    df["ss_falling"] = f < f.shift(1)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
