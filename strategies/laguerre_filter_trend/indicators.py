"""Laguerre filter trend (John Ehlers, "Time Warp, Without Space Travel").

Four-element Laguerre filter with gamma=0.8 applied to hl2=(h+l)/2:

    L0 = (1-g) * x + g * L0[1]
    L1 = -g * L0 + L0[1] + g * L1[1]
    L2 = -g * L1 + L1[1] + g * L2[1]
    L3 = -g * L2 + L2[1] + g * L3[1]
    Filt = (L0 + 2*L1 + 2*L2 + L3) / 6

The Laguerre filter is an IIR low-pass with very little lag for its
smoothing: it tracks price closely in trends and flattens in chop.
Columns:

    laguerre -- the filter output Filt
    hl2      -- (h+l)/2 input
    atr      -- Wilder ATR(14) for the risk layer

No lookahead: every recursion on bar j uses data through bar j only.
Filter state is seeded with the first hl2 value, so the filter is
defined from bar 0 (it needs ~tens of bars to settle after a step,
well inside WARMUP=60).
"""

import numpy as np
import pandas as pd

from strategies import base as B

GAMMA = 0.8  # shipped default


def laguerre_filter(x: pd.Series, gamma: float = GAMMA) -> pd.Series:
    """Four-element Laguerre filter of a price series."""
    xv = x.to_numpy(dtype=float)
    m = len(xv)
    out = np.full(m, np.nan)
    if m == 0:
        return pd.Series(out, index=x.index, name="laguerre")
    g = float(gamma)
    l0 = l1 = l2 = l3 = float(xv[0])
    for i in range(m):
        v = float(xv[i])
        l0_new = (1.0 - g) * v + g * l0
        l1_new = -g * l0_new + l0 + g * l1
        l2_new = -g * l1_new + l1 + g * l2
        l3_new = -g * l2_new + l2 + g * l3
        l0, l1, l2, l3 = l0_new, l1_new, l2_new, l3_new
        out[i] = (l0 + 2.0 * l1 + 2.0 * l2 + l3) / 6.0
    return pd.Series(out, index=x.index, name="laguerre")


def add_indicators(df: pd.DataFrame, gamma: float = GAMMA) -> pd.DataFrame:
    df = df.copy()
    hl2 = (df["h"] + df["l"]) / 2.0
    df["hl2"] = hl2
    df["laguerre"] = laguerre_filter(hl2, gamma)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
