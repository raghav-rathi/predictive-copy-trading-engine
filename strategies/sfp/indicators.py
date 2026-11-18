"""Swing Failure Pattern (SFP) indicators.

Causal 5-bar swing pivots (centre+2 confirmation): a swing high at
centre j iff h[j] is the max of h[j-2..j+2] (strictly greater than
both left neighbours, >= both right neighbours); a swing low iff
l[j] is the min of l[j-2..j+2] (strictly less than both left
neighbours, <= both right neighbours). Pivots are recorded at the
CONFIRMATION bar (centre+2), never at the centre bar, via an
explicit loop: at bar i only centre i-2 can confirm, using bars
i-4..i. The most recent confirmed swing high/low is forward-filled
as swing_high / swing_low (NaN until the first pivot confirms).

Columns:
    swing_high -- last confirmed swing-high level
    swing_low  -- last confirmed swing-low level
    vol_ma20   -- SMA(volume, 20)
    atr        -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

VOL_MA_N = 20
ATR_N = 14

INDICATOR_COLS = ["swing_high", "swing_low", "vol_ma20", "atr"]


def confirmed_pivots(h: pd.Series, l: pd.Series):
    """Causal 5-bar pivots. Returns (swing_high, swing_low) numpy
    arrays, NaN until the first pivot of each kind confirms."""
    hv = h.to_numpy(dtype=float)
    lv = l.to_numpy(dtype=float)
    n = len(hv)
    sh = np.full(n, np.nan)
    sl = np.full(n, np.nan)
    cur_h = np.nan
    cur_l = np.nan
    for i in range(n):
        j = i - 2
        if j >= 2:
            if (hv[j] > hv[j - 1] and hv[j] > hv[j - 2]
                    and hv[j] >= hv[j + 1] and hv[j] >= hv[j + 2]):
                cur_h = hv[j]
            if (lv[j] < lv[j - 1] and lv[j] < lv[j - 2]
                    and lv[j] <= lv[j + 1] and lv[j] <= lv[j + 2]):
                cur_l = lv[j]
        sh[i] = cur_h
        sl[i] = cur_l
    return sh, sl


def add_indicators(df: pd.DataFrame, vol_n: int = VOL_MA_N,
                   atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    sh, sl = confirmed_pivots(df["h"], df["l"])
    df["swing_high"] = sh
    df["swing_low"] = sl
    df["vol_ma20"] = B.sma(df["v"], vol_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    return df
