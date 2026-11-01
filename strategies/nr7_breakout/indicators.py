"""NR7 narrow-range indicators (Toby Crabel).

An NR7 bar's high-low range is narrower than each of the previous six
bars' ranges: volatility has contracted and an expansion (breakout)
usually follows. This module tracks the most recent NR7 bar's high and
low, valid for 24 bars after the NR7 bar; older setups expire.

Columns:
    nr7_high -- most recent live NR7 bar's high (NaN when no live setup)
    nr7_low  -- most recent live NR7 bar's low
    atr      -- Wilder ATR(14) for the risk layer

All values use only bars up to and including the current bar, so
the indicators are strictly causal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

WINDOW = 7
VALID_BARS = 24


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    rng = (df["h"] - df["l"]).to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    is_nr7 = np.zeros(n, dtype=bool)
    for i in range(6, n):
        if rng[i] < rng[i - 6:i].min():
            is_nr7[i] = True
    high = np.full(n, np.nan)
    low = np.full(n, np.nan)
    last = None  # (high, low, bar)
    for i in range(n):
        if is_nr7[i]:
            last = (h[i], l[i], i)
        if last is not None and i - last[2] <= VALID_BARS:
            high[i], low[i] = last[0], last[1]
    df["nr7_high"] = high
    df["nr7_low"] = low
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
