"""Market-structure Break of Structure (BOS) indicators (causal, no lookahead).

A 5-bar pivot high at bar j is a high that is the maximum of the
5 bars centred on j (h[j-2..j+2]); a pivot low is the mirror
minimum. A pivot is only *confirmed* once the 2 bars to its
right have closed, so at bar i the only pivots usable are those
with centre j <= i - 2. The most recent confirmed swing high /
swing low are carried forward as ``swing_high`` / ``swing_low``.

A break is a *close* beyond the level, not a wick: ``break_up``
when c[i] > swing_high[i] while c[i-1] <= swing_high[i], and
``break_down`` mirrored. A broken level is spent by the cross
condition (a close that stays beyond it does not re-fire).

``bos_dir`` is the BOS-continuation event the strategy trades:
a break in the same direction as the previous break — i.e. an
uptrend leg confirmed by a higher high (two consecutive upward
breaks), or the mirror. The first break in a new direction only
sets the trend state; it does not itself enter. This follows
the spec: long entry requires a close above the prior swing
high while the last structure break was also upward.

Columns:
    swing_high, swing_low -- most recent confirmed swing levels
    break_up, break_down  -- raw close-cross breaks (any direction)
    bos_dir               -- +1 BOS-continuation up, -1 down, else 0
    atr                   -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT_HALF = 2  # 5-bar pivots: 2 bars each side


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)

    pivot_high = np.zeros(n, dtype=bool)
    pivot_low = np.zeros(n, dtype=bool)
    for j in range(PIVOT_HALF, n - PIVOT_HALF):
        if h[j] == np.max(h[j - PIVOT_HALF:j + PIVOT_HALF + 1]):
            pivot_high[j] = True
        if l[j] == np.min(l[j - PIVOT_HALF:j + PIVOT_HALF + 1]):
            pivot_low[j] = True

    swing_high = np.full(n, np.nan)
    swing_low = np.full(n, np.nan)
    break_up = np.zeros(n, dtype=bool)
    break_down = np.zeros(n, dtype=bool)
    bos_dir = np.zeros(n, dtype=int)

    last_sh = None
    last_sl = None
    last_break = 0  # +1 up, -1 down, 0 none yet
    for i in range(n):
        # Confirm pivots whose 2 right-hand bars have now closed.
        if i >= PIVOT_HALF:
            j = i - PIVOT_HALF
            if pivot_high[j]:
                last_sh = h[j]
            if pivot_low[j]:
                last_sl = l[j]
        if last_sh is not None:
            swing_high[i] = last_sh
        if last_sl is not None:
            swing_low[i] = last_sl
        if last_sh is not None and i > 0 and c[i] > last_sh and c[i - 1] <= last_sh:
            break_up[i] = True
        if last_sl is not None and i > 0 and c[i] < last_sl and c[i - 1] >= last_sl:
            break_down[i] = True
        # BOS continuation: break in the same direction as the last break.
        if break_up[i] and last_break == 1:
            bos_dir[i] = 1
        elif break_down[i] and last_break == -1:
            bos_dir[i] = -1
        if break_up[i]:
            last_break = 1
        elif break_down[i]:
            last_break = -1

    df["swing_high"] = swing_high
    df["swing_low"] = swing_low
    df["break_up"] = break_up
    df["break_down"] = break_down
    df["bos_dir"] = bos_dir
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
