"""Rolling volume-profile POC indicators.

Over the trailing 168 bars including the current bar, the window's
price range (min low -> max high) is split into 24 equal bins and
each bar's volume is assigned to the bin containing its close. POC
is the price level where the most volume traded, estimated as the
volume-weighted mean close of the highest-volume bin (this coincides
with the bin midpoint when closes are spread evenly across the bin).
VAH/VAL are the bounds of
the smallest contiguous bin set around the POC bin holding at least
70% of the window's volume, grown greedily outward one bin at a time
(taking the heavier neighbouring bin first; ties go right). A
zero-range window collapses POC/VAH/VAL to the close. Only data
through bar i's close is used for bar i's levels.
"""

import numpy as np
import pandas as pd

from strategies.base import atr

WINDOW_BARS = 168
N_BINS = 24
VALUE_AREA_FRAC = 0.70

INDICATOR_COLS = [
    "vp_poc",
    "vp_vah",
    "vp_val",
    "atr14",
]


def _profile_poc_vah_val(lows, highs, closes, vols):
    """POC / VAH / VAL for one window of bars."""
    lo = float(np.min(lows))
    hi = float(np.max(highs))
    if hi <= lo:
        px = float(closes[-1])
        return px, px, px
    edges = np.linspace(lo, hi, N_BINS + 1)
    idx = np.clip(np.digitize(closes, edges[1:-1]), 0, N_BINS - 1)
    vol_by_bin = np.bincount(idx, weights=vols, minlength=N_BINS)
    poc_bin = int(np.argmax(vol_by_bin))
    # POC is the price level where the most volume traded: the
    # volume-weighted mean close of the modal bin. This coincides
    # with the bin midpoint when closes are spread evenly across
    # the bin, and degrades gracefully to the exact traded price
    # when every close in the bin is identical (e.g. flat data,
    # where a geometric midpoint would sit half a bin-width away
    # from the price and flag a spurious signal).
    in_poc = idx == poc_bin
    w = vols[in_poc]
    if len(w) and float(np.sum(w)) > 0:
        poc = float(np.average(closes[in_poc], weights=w))
    else:
        poc = float((edges[poc_bin] + edges[poc_bin + 1]) / 2.0)
    target = VALUE_AREA_FRAC * float(np.sum(vols))
    lo_b = hi_b = poc_bin
    acc = float(vol_by_bin[poc_bin])
    while acc < target and (lo_b > 0 or hi_b < N_BINS - 1):
        left_vol = float(vol_by_bin[lo_b - 1]) if lo_b > 0 else -1.0
        right_vol = float(vol_by_bin[hi_b + 1]) if hi_b < N_BINS - 1 else -1.0
        if right_vol >= left_vol:
            hi_b += 1
            acc += float(vol_by_bin[hi_b])
        else:
            lo_b -= 1
            acc += float(vol_by_bin[lo_b])
    return poc, float(edges[hi_b + 1]), float(edges[lo_b])


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)
    poc = np.full(n, np.nan)
    vah = np.full(n, np.nan)
    val = np.full(n, np.nan)
    for i in range(WINDOW_BARS - 1, n):
        sl = slice(i - WINDOW_BARS + 1, i + 1)
        poc[i], vah[i], val[i] = _profile_poc_vah_val(l[sl], h[sl], c[sl], v[sl])
    df["vp_poc"] = poc
    df["vp_vah"] = vah
    df["vp_val"] = val
    df["atr14"] = atr(df["h"], df["l"], df["c"], 14)
    return df
