"""Rolling TPO (time-price opportunity) market-profile indicators.

Over the trailing 168 bars including the current bar, the window's
price range (min low -> max high) is split into 24 equal bins. Each
bar contributes ONE TPO to the bin containing its midpoint
((h + l) / 2) -- this is price-TIME, not volume: a bar counts once
regardless of how much volume it traded. POC is the midpoint of the
bin with the most TPOs (ties go to the lowest bin). The value area is
the smallest contiguous set of bins around the POC bin holding at
least 70% of the window's TPOs, grown greedily outward one bin at a
time (taking the heavier neighbouring bin first; ties go right).
VAH / VAL are the upper / lower edges of that bin set. A zero-range
window collapses POC / VAH / VAL to the close. Only data through bar
i's close is used for bar i's levels.
"""

import numpy as np
import pandas as pd

WINDOW_BARS = 168
N_BINS = 24
VALUE_AREA_FRAC = 0.70

INDICATOR_COLS = [
    "tpo_poc",
    "tpo_vah",
    "tpo_val",
]


def _profile_poc_vah_val(lows, highs, mids):
    """POC / VAH / VAL for one window of bars."""
    lo = float(np.min(lows))
    hi = float(np.max(highs))
    if hi <= lo:
        px = float(mids[-1])
        return px, px, px
    width = (hi - lo) / N_BINS
    idx = np.clip(((mids - lo) / width).astype(int), 0, N_BINS - 1)
    counts = np.bincount(idx, minlength=N_BINS).astype(float)
    poc_bin = int(np.argmax(counts))
    total = float(counts.sum())
    target = VALUE_AREA_FRAC * total
    lo_bin = hi_bin = poc_bin
    covered = float(counts[poc_bin])
    while covered < target and (lo_bin > 0 or hi_bin < N_BINS - 1):
        left = counts[lo_bin - 1] if lo_bin > 0 else -1.0
        right = counts[hi_bin + 1] if hi_bin < N_BINS - 1 else -1.0
        if right >= left:
            hi_bin += 1
            covered += counts[hi_bin]
        else:
            lo_bin -= 1
            covered += counts[lo_bin]
    poc = lo + (poc_bin + 0.5) * width
    vah = lo + (hi_bin + 1) * width
    val = lo + lo_bin * width
    return poc, vah, val


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    lows = df["l"].to_numpy(dtype=float)
    highs = df["h"].to_numpy(dtype=float)
    mids = ((df["h"] + df["l"]) / 2).to_numpy(dtype=float)
    poc = np.full(n, np.nan)
    vah = np.full(n, np.nan)
    val = np.full(n, np.nan)
    for i in range(WINDOW_BARS - 1, n):
        s = i - WINDOW_BARS + 1
        poc[i], vah[i], val[i] = _profile_poc_vah_val(
            lows[s:i + 1], highs[s:i + 1], mids[s:i + 1]
        )
    df["tpo_poc"] = poc
    df["tpo_vah"] = vah
    df["tpo_val"] = val
    return df
