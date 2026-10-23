"""RSI(14) divergence indicators: confirmed swing pivots + RSI values.

Pivot detection with confirmation lag k (lookahead-free): a swing HIGH
at bar p is marked iff h[p] == max(h[p-k .. p+k]); a swing LOW iff
l[p] == min(l[p-k .. p+k]). The pivot is only *confirmed* (usable) at
the close of bar p+k, so everything signals.py reads on bar j was known
at bar j's close.

Columns:

    rsi14            -- Wilder RSI(14) of close (B.rsi)
    pivot_high       -- True at swing-high center bars (left=right=3)
    pivot_low        -- True at swing-low center bars (left=right=3)
    pivot_high_price -- h at swing-high centers, NaN elsewhere
    pivot_high_rsi   -- rsi14 at swing-high centers, NaN elsewhere
    pivot_low_price  -- l at swing-low centers, NaN elsewhere
    pivot_low_rsi    -- rsi14 at swing-low centers, NaN elsewhere
    atr              -- Wilder ATR(14) for the risk layer

Flat ties (two adjacent bars both equal to the window max/min) are
collapsed to the first bar of the tied run, so a flat top/bottom does
not produce a degenerate one-bar-apart "pivot pair".
"""

import numpy as np
import pandas as pd

from strategies import base as B

RSI_N = 14
PIVOT_LEFT = 3
PIVOT_RIGHT = 3
ATR_LEN = 14


def _pivot_low(l: pd.Series, k: int) -> pd.Series:
    w = 2 * k + 1
    win_min = l.rolling(w, center=True, min_periods=w).min()
    is_pivot = (l == win_min).fillna(False)
    # collapse flat ties: keep the first bar of each tied run
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
    rsi_n: int = RSI_N,
    pivot_k: int = PIVOT_LEFT,
    atr_len: int = ATR_LEN,
) -> pd.DataFrame:
    df = df.copy()
    rsi = B.rsi(df["c"], rsi_n)
    df["rsi14"] = rsi

    pl = _pivot_low(df["l"], pivot_k)
    ph = _pivot_high(df["h"], pivot_k)
    df["pivot_low"] = pl.astype(bool)
    df["pivot_high"] = ph.astype(bool)
    df["pivot_low_price"] = df["l"].where(pl, np.nan)
    df["pivot_low_rsi"] = rsi.where(pl, np.nan)
    df["pivot_high_price"] = df["h"].where(ph, np.nan)
    df["pivot_high_rsi"] = rsi.where(ph, np.nan)

    df["atr"] = B.atr(df["h"], df["l"], df["c"], atr_len)
    df.attrs["pivot_k"] = pivot_k
    return df
