"""Anchored VWAP indicators (Shannon).

Idea in plain terms: a volume-weighted average price that restarts at the
most recent major swing extreme, instead of resetting every calendar day.
The swing extreme is the point the big participants would have defended,
so price reclaiming that line with the line itself rising is treated as
an institutional bid returning.

Mechanics:
  - 51-bar fractal: bar j is a swing low when l[j] is the minimum of
    l[j-25..j+25] (swing high mirrors this with h). The extreme is only
    *confirmed* at bar j+25, and the anchor is used from that bar on.
  - AVWAP from anchor a to bar i: sum(typical*v)[a..i] / sum(v)[a..i],
    computed in O(n) via cumulative sums. typical = (h+l+c)/3.
  - Two anchors are tracked (bull = most recent confirmed swing low,
    bear = most recent confirmed swing high); the *active* anchor is
    whichever was confirmed most recently.

No lookahead: every value at bar i uses only bars <= i; the 25-bar
confirmation lag is explicit and tested.
"""

import numpy as np
import pandas as pd

from strategies import base as B

FRACTAL_HALF = 25  # swing window half-length -> 51-bar fractal


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    l = df["l"].to_numpy()
    h = df["h"].to_numpy()
    c = df["c"].to_numpy()
    v = df["v"].to_numpy()

    tp = (h + l + c) / 3.0
    cpv = np.cumsum(tp * v)          # cumulative price*volume
    cv = np.cumsum(v)               # cumulative volume

    k = FRACTAL_HALF
    win = 2 * k + 1
    ls, hs = pd.Series(l), pd.Series(h)
    # bar j is a swing low iff the window minimum sits at the window
    # centre; argmin breaks ties to the first occurrence so flat runs
    # do not manufacture anchors
    is_low = (
        ls.rolling(win, center=True, min_periods=win)
        .apply(lambda w: 1.0 if np.argmin(w) == k else 0.0, raw=True)
        .fillna(0.0)
        .to_numpy()
        .astype(bool)
    )
    is_high = (
        hs.rolling(win, center=True, min_periods=win)
        .apply(lambda w: 1.0 if np.argmax(w) == k else 0.0, raw=True)
        .fillna(0.0)
        .to_numpy()
        .astype(bool)
    )

    avwap = np.full(n, np.nan)
    avwap_bull = np.full(n, np.nan)
    avwap_bear = np.full(n, np.nan)
    anchor_idx = np.full(n, -1, dtype=np.int64)

    bull_j, bear_j = -1, -1          # center bars of most recent confirmed extremes
    bull_t, bear_t = -1, -1          # bars at which they were confirmed

    for i in range(n):
        j = i - k
        if j >= 0:
            if is_low[j]:
                bull_j, bull_t = j, i
            if is_high[j]:
                bear_j, bear_t = j, i

        if bull_j >= 0:
            prev = cpv[bull_j - 1] if bull_j > 0 else 0.0
            prevv = cv[bull_j - 1] if bull_j > 0 else 0.0
            den = cv[i] - prevv
            avwap_bull[i] = (cpv[i] - prev) / den if den > 0 else np.nan
        if bear_j >= 0:
            prev = cpv[bear_j - 1] if bear_j > 0 else 0.0
            prevv = cv[bear_j - 1] if bear_j > 0 else 0.0
            den = cv[i] - prevv
            avwap_bear[i] = (cpv[i] - prev) / den if den > 0 else np.nan

        # active anchor = the most recently confirmed extreme
        if bull_t >= bear_t and bull_j >= 0:
            avwap[i] = avwap_bull[i]
            anchor_idx[i] = bull_j
        elif bear_j >= 0:
            avwap[i] = avwap_bear[i]
            anchor_idx[i] = bear_j

    df["avwap"] = avwap
    df["avwap_bull"] = avwap_bull
    df["avwap_bear"] = avwap_bear
    df["avwap_anchor"] = anchor_idx
    return df
