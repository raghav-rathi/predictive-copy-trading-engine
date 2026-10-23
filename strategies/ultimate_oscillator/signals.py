"""Ultimate Oscillator divergence signals -- Williams' three-step method.

Mechanized version of Larry Williams' own divergence method from
"The Ultimate Oscillator" (Technical Analysis of Stocks & Commodities,
April 1985):

  Bullish:
    1. Price makes a LOWER low while UO makes a HIGHER low, with UO
       dipping below 30 at some bar between the two lows.
    2. Trigger: long when UO crosses ABOVE the highest UO reading
       recorded between the two lows ("rise above the divergence high").
    3. Exit: close the long when UO crosses above 70.

  Bearish (mirror):
    1. Price makes a HIGHER high while UO makes a LOWER high, with UO
       exceeding 70 at some bar between the two highs.
    2. Trigger: short when UO crosses BELOW the lowest UO reading
       recorded between the two highs.
    3. Exit: cover the short when UO crosses below 30.

Pivots are CONFIRMED only (left=3, right=3 bars): a pivot at bar p is
usable on bars i >= p+3, so there is no lookahead. The price reference
at a UO pivot bar is the bar's low (troughs) / high (peaks).

The pending setup is re-evaluated from the latest two confirmed pivots
each time a new pivot confirms; a non-divergent latest pair cancels the
pending setup, and each setup fires at most once.

Signal columns are boolean, no NaN. A signal on bar i uses data through
bar i's close only; the harness executes at bar i+1's open.
"""

import numpy as np
import pandas as pd

from strategies.base import crossed_above, crossed_below

LB = 3                # pivot left bars (fixed a priori)
RB = 3                # pivot right bars = confirmation delay (fixed a priori)
UO_OVERSOLD = 30.0    # fixed a priori (Williams)
UO_OVERBOUGHT = 70.0  # fixed a priori (Williams)


def _all_pivots(uo: np.ndarray, lb: int = LB, rb: int = RB, kind: str = "low"):
    """All swing pivots of the UO series.

    A pivot at bar p is the UNIQUE extremum of the window [p-lb, p+rb].
    ``kind`` is "low" (troughs) or "high" (peaks). Windows containing
    NaN are skipped.
    """
    n = len(uo)
    out = []
    for p in range(lb, n - rb):
        w = uo[p - lb : p + rb + 1]
        if np.isnan(w).any():
            continue
        v = w[lb]
        if kind == "low":
            if v == w.min() and int((w == v).sum()) == 1:
                out.append(p)
        elif kind == "high":
            if v == w.max() and int((w == v).sum()) == 1:
                out.append(p)
        else:
            raise ValueError(f"bad pivot kind {kind!r}")
    return out


def _confirmed(pivots, i: int, rb: int = RB):
    """Pivots confirmed as of bar i: pivot bar p is usable once p + rb <= i."""
    return [p for p in pivots if p + rb <= i]


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    uo = df["uo"].to_numpy(dtype=float)
    lo = df["l"].to_numpy(dtype=float)
    hi = df["h"].to_numpy(dtype=float)
    n = len(df)

    low_piv = _all_pivots(uo, LB, RB, "low")
    high_piv = _all_pivots(uo, LB, RB, "high")

    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)

    uo_s = pd.Series(uo)
    # crossed_* needs Series on both sides; build constant threshold series.
    hi_thr = pd.Series(UO_OVERBOUGHT, index=uo_s.index)
    lo_thr = pd.Series(UO_OVERSOLD, index=uo_s.index)
    long_exit = crossed_above(uo_s, hi_thr).fillna(False).to_numpy().astype(bool)
    short_exit = crossed_below(uo_s, lo_thr).fillna(False).to_numpy().astype(bool)

    li = 0        # low pivots confirmed so far
    hi_ptr = 0    # high pivots confirmed so far
    pend_long = None    # span-max UO of the armed bullish setup
    pend_short = None   # span-min UO of the armed bearish setup

    for i in range(n):
        # Newly confirmed low pivots -> re-evaluate on the latest pair.
        new_low = False
        while li < len(low_piv) and low_piv[li] + RB <= i:
            li += 1
            new_low = True
        if new_low and li >= 2:
            p1, p2 = low_piv[li - 2], low_piv[li - 1]
            if (
                lo[p2] < lo[p1]
                and uo[p2] > uo[p1]
                and np.nanmin(uo[p1 : p2 + 1]) < UO_OVERSOLD
            ):
                pend_long = float(np.nanmax(uo[p1 + 1 : p2]))
            else:
                pend_long = None
        # Newly confirmed high pivots -> re-evaluate the bearish setup.
        new_high = False
        while hi_ptr < len(high_piv) and high_piv[hi_ptr] + RB <= i:
            hi_ptr += 1
            new_high = True
        if new_high and hi_ptr >= 2:
            p1, p2 = high_piv[hi_ptr - 2], high_piv[hi_ptr - 1]
            if (
                hi[p2] > hi[p1]
                and uo[p2] < uo[p1]
                and np.nanmax(uo[p1 : p2 + 1]) > UO_OVERBOUGHT
            ):
                pend_short = float(np.nanmin(uo[p1 + 1 : p2]))
            else:
                pend_short = None
        # Triggers: crosses evaluated on bars i-1 and i only (no lookahead).
        if i > 0 and pend_long is not None and not (np.isnan(uo[i]) or np.isnan(uo[i - 1])):
            if uo[i] > pend_long >= uo[i - 1]:
                long_entry[i] = True
                pend_long = None  # one entry per setup
        if i > 0 and pend_short is not None and not (np.isnan(uo[i]) or np.isnan(uo[i - 1])):
            if uo[i] < pend_short <= uo[i - 1]:
                short_entry[i] = True
                pend_short = None  # one entry per setup

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
