"""Volume profile value-area indicators.

A rolling 168-bar composite volume profile with 24 equal price bins
spanning the window's [min low, max high]:

* each bar's volume is distributed uniformly across the bins its
  [low, high] range touches (vectorized with a difference-array
  trick: +share at the first touched bin, -share after the last,
  then cumsum). Uses only bars up to and including bar i — causal.
* POC = bin with the most volume.
* Value area: expand outward from the POC, each step adding the
  adjacent bin with the most volume, until >= 70% of the window's
  volume is captured. VAH = top edge of the highest VA bin,
  VAL = bottom edge of the lowest VA bin.

Columns: vp_val, vp_vah, vp_poc (POC price = bin center).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

WINDOW = 168  # bars in the rolling composite profile
BINS = 24  # price bins per profile
VA_PCT = 0.70  # value-area volume fraction


def _profile_at(l_w: np.ndarray, h_w: np.ndarray, v_w: np.ndarray):
    """(val, vah, poc_price) for one window slice."""
    lo = float(np.min(l_w))
    hi = float(np.max(h_w))
    width = (hi - lo) / BINS
    if not np.isfinite(width) or width <= 0:
        return lo, hi, lo
    bl = np.clip(((l_w - lo) / width).astype(np.int64), 0, BINS - 1)
    bh = np.clip(((h_w - lo) / width).astype(np.int64), 0, BINS - 1)
    share = v_w / (bh - bl + 1.0)
    diff = np.zeros(BINS + 1)
    np.add.at(diff, bl, share)
    np.add.at(diff, np.clip(bh + 1, 0, BINS), -share)
    vol = np.cumsum(diff[:BINS])
    total = float(vol.sum())
    poc = int(np.argmax(vol))
    edges = np.linspace(lo, hi, BINS + 1)

    va = float(vol[poc])
    lo_b, hi_b = poc, poc
    target = VA_PCT * total
    while va < target and (lo_b > 0 or hi_b < BINS - 1):
        left = float(vol[lo_b - 1]) if lo_b > 0 else -1.0
        right = float(vol[hi_b + 1]) if hi_b < BINS - 1 else -1.0
        if right >= left and hi_b < BINS - 1:
            hi_b += 1
            va += float(vol[hi_b])
        elif lo_b > 0:
            lo_b -= 1
            va += float(vol[lo_b])
        else:
            break
    val = float(edges[lo_b])
    vah = float(edges[hi_b + 1])
    poc_px = float((edges[poc] + edges[poc + 1]) / 2.0)
    return val, vah, poc_px


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    l = df["l"].to_numpy(float)
    h = df["h"].to_numpy(float)
    v = df["v"].to_numpy(float)
    n = len(df)

    val = np.full(n, np.nan)
    vah = np.full(n, np.nan)
    poc = np.full(n, np.nan)
    for i in range(WINDOW - 1, n):
        j0 = i - WINDOW + 1
        val[i], vah[i], poc[i] = _profile_at(l[j0 : i + 1], h[j0 : i + 1], v[j0 : i + 1])

    out["vp_val"] = val
    out["vp_vah"] = vah
    out["vp_poc"] = poc
    return out
