"""Diamond top/bottom indicators (causal).

At bar i the pattern is a window ending at bar i-1 (the breakout
bar itself is never part of the pattern): an expanding phase
followed by a contracting phase, total length 15-40 bars. The
apex is the widest bar-range inside the window. Expansion
requires the apex range to exceed the start range by 30% with
highs rising / lows falling into the apex; contraction requires
the end range to fall below 70% of the apex range with highs
falling / lows rising out of the apex. A breakout close beyond
the converging-phase boundary (max high / min low from the apex
through bar i-1) on volume above 1.2x the pattern average fires.

Columns:
    diamond_dir -- +1 on a long-breakout bar, -1 on a
                   short-breakout bar, else 0
    bar_range   -- high - low per bar (the pattern's raw input)
    atr         -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

MIN_LEN = 15
MAX_LEN = 40
MIN_PHASE = 5
EXPAND_MULT = 1.3
CONTRACT_MULT = 0.7
VOL_MULT = 1.2


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)
    r = h - l

    direction = np.zeros(n, dtype=int)
    for i in range(n):
        if i < MIN_LEN:
            continue
        # pattern window [s, i-1]; length i-s in [MIN_LEN, MAX_LEN]
        for s in range(max(0, i - MAX_LEN), i - MIN_LEN + 1):
            lo, hi = s + MIN_PHASE, i - 1 - MIN_PHASE
            if hi < lo:
                continue
            a = lo + int(np.argmax(r[lo:hi + 1]))
            if r[a] <= EXPAND_MULT * r[s]:
                continue
            if r[i - 1] >= CONTRACT_MULT * r[a]:
                continue
            # highs rising / lows falling into the apex
            if not (
                np.max(h[a - 2:a + 1]) > np.max(h[s:s + 3])
                and np.min(l[a - 2:a + 1]) < np.min(l[s:s + 3])
            ):
                continue
            # highs falling / lows rising out of the apex
            if not (
                np.max(h[i - 3:i]) < np.max(h[a - 2:a + 1])
                and np.min(l[i - 3:i]) > np.min(l[a - 2:a + 1])
            ):
                continue
            avg_vol = float(np.mean(v[s:i]))
            if not (np.isfinite(avg_vol) and avg_vol > 0 and v[i] > VOL_MULT * avg_vol):
                continue
            if c[i] > np.max(h[a:i]):
                direction[i] = 1
            elif c[i] < np.min(l[a:i]):
                direction[i] = -1
            else:
                continue
            break

    df["diamond_dir"] = direction
    df["bar_range"] = r
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
