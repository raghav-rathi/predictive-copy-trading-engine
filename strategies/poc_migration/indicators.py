"""Rolling volume-profile Point of Control (POC) trend.

For each bar i, the profile window is the last 50 bars (i-49..i). The
window's price range (min low to max high) is split into 20 equal bins;
each bar's volume is assigned to the bin containing its close, and the
POC is the centre of the bin with the most volume (ties: lowest bin).
POC is therefore a causal, volume-weighted "where business was done"
level, recomputed every bar as the window rolls.

Columns:
    poc           -- rolling 50-bar POC (NaN before bar 49)
    poc_change_10 -- poc minus poc 10 bars ago (NaN before bar 59)
    poc_dir       -- +1 if poc rose vs 10 bars ago, -1 if it fell,
                     else 0
    atr           -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

WINDOW = 50
BINS = 20
LAG = 10


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)
    n = len(df)
    poc = np.full(n, np.nan)
    for i in range(WINDOW - 1, n):
        lo = l[i - WINDOW + 1:i + 1].min()
        hi = h[i - WINDOW + 1:i + 1].max()
        if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
            poc[i] = c[i]
            continue
        edges = np.linspace(lo, hi, BINS + 1)
        idx = np.searchsorted(edges, c[i - WINDOW + 1:i + 1], side="right") - 1
        idx = np.clip(idx, 0, BINS - 1)
        volsum = np.bincount(idx, weights=v[i - WINDOW + 1:i + 1], minlength=BINS)
        best = int(np.argmax(volsum))
        poc[i] = (edges[best] + edges[best + 1]) / 2.0
    poc_s = pd.Series(poc, index=df.index)
    df["poc"] = poc_s
    df["poc_change_10"] = poc_s - poc_s.shift(LAG)
    df["poc_dir"] = np.where(
        df["poc_change_10"].fillna(0) > 0, 1,
        np.where(df["poc_change_10"].fillna(0) < 0, -1, 0),
    ).astype(int)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
