"""OBV divergence indicators (Granville On-Balance Volume + price divergence).

On-Balance Volume (Granville, 1963): obv = cumsum(sign(c - c.shift(1)) * v);
an unchanged close adds 0. OBV is a cumulative volume-pressure gauge — it
rises when volume flows into up-closes and falls when volume flows into
down-closes.

Pivot detection with confirmation lag k (lookahead-free): a pivot at bar i
is confirmed at the close of bar i+k, so everything a signal reads on bar j
was known at bar j's close. pivot_low[i+k] is True when l[i] is the unique
minimum of l[i-k .. i+k]; pivot_high likewise with the maximum of h.

Pivot bars store their price and OBV values in `pivot_low_price` /
`pivot_low_obv` / `pivot_high_price` / `pivot_high_obv` (NaN elsewhere) for
the divergence comparison in signals.py.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_LEN = 14
PIVOT_K = 10


def _pivot_low(l: pd.Series, k: int) -> pd.Series:
    w = 2 * k + 1
    win_min = l.rolling(w, center=True, min_periods=w).min()
    is_pivot = (l == win_min).fillna(False)
    # drop duplicates from flat ties: keep the first bar of each tied run
    is_pivot = is_pivot & ~(is_pivot.shift(1).fillna(False))
    return is_pivot


def _pivot_high(h: pd.Series, k: int) -> pd.Series:
    w = 2 * k + 1
    win_max = h.rolling(w, center=True, min_periods=w).max()
    is_pivot = (h == win_max).fillna(False)
    is_pivot = is_pivot & ~(is_pivot.shift(1).fillna(False))
    return is_pivot


def add_indicators(
    df: pd.DataFrame,
    pivot_k: int = PIVOT_K,
    atr_len: int = ATR_LEN,
) -> pd.DataFrame:
    df = df.copy()
    # OBV: unchanged close contributes 0 (diff -> NaN -> 0, sign 0 anyway)
    dc = df["c"].diff()
    df["obv"] = (np.sign(dc.fillna(0.0)) * df["v"]).cumsum()

    pl = _pivot_low(df["l"], pivot_k)
    ph = _pivot_high(df["h"], pivot_k)
    df["pivot_low_price"] = df["l"].where(pl, np.nan)
    df["pivot_low_obv"] = df["obv"].where(pl, np.nan)
    df["pivot_high_price"] = df["h"].where(ph, np.nan)
    df["pivot_high_obv"] = df["obv"].where(ph, np.nan)

    df["atr"] = B.atr(df["h"], df["l"], df["c"], atr_len)
    df.attrs["pivot_k"] = pivot_k
    return df
