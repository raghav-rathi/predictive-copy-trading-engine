"""Anchored VWAP indicators (causal, no lookahead).

VWAP anchored (reset) at the most recent confirmed 20-bar
swing pivot, one series per pivot type:

    avwap_low  -- VWAP cumulated from the most recent swing-low
                  pivot bar (typical price * volume / volume).
    avwap_high -- VWAP cumulated from the most recent swing-high
                  pivot bar.

A bar j is a swing-high pivot when its high is the maximum
high over the 20-bar window centred on j (10 bars each side);
a swing-low pivot is the mirror with the minimum low. The
pivot is only *activated* at bar j + 10, once its right-hand
window is fully observed, so no AVWAP value at bar i ever
uses data beyond bar i. Before any pivot is confirmed the
series fall back to a VWAP cumulated from bar 0, so the
columns contain no NaN at all. Activation recomputes the
cumulative sums from the pivot bar through the activation
bar — all bars <= the activation bar — which keeps the
series truncation-safe: appending a future bar never changes
an earlier AVWAP value.

Columns:
    avwap_low, avwap_high -- anchored VWAP series
    avwap_low_rising     -- avwap_low above its value 5 bars ago
    avwap_high_falling   -- avwap_high below its value 5 bars ago
    atr                  -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

LEFT = 10
RIGHT = 10
RISE_BARS = 5


def _avwap_series(tp, v, anchors):
    """Cumulate tp*v / v from each anchor; anchors[i] is the
    anchor bar in force at bar i (or None for bar 0 fallback
    handled by the caller passing anchor 0)."""
    n = len(tp)
    out = np.full(n, np.nan)
    cur_anchor = None
    cum_pv = 0.0
    cum_v = 0.0
    for i in range(n):
        a = anchors[i]
        if a is not None and a != cur_anchor:
            # (Re)start cumulation at the anchor bar, summing
            # through the current bar — all bars <= i.
            cur_anchor = a
            seg_v = v[a:i + 1]
            seg_pv = tp[a:i + 1] * seg_v
            cum_v = float(seg_v.sum())
            cum_pv = float(seg_pv.sum())
        elif cur_anchor is None:
            cur_anchor = 0
            cum_v = float(v[i])
            cum_pv = float(tp[i] * v[i])
        else:
            cum_v += float(v[i])
            cum_pv += float(tp[i] * v[i])
        out[i] = cum_pv / cum_v if cum_v > 0 else tp[i]
    return out


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)
    tp = (h + l + c) / 3.0
    n = len(df)

    # Anchor in force at each bar; None means "not yet set",
    # which _avwap_series treats as anchor 0.
    anchor_low = np.full(n, None, dtype=object)
    anchor_high = np.full(n, None, dtype=object)
    cur_low = None
    cur_high = None
    for i in range(n):
        j = i - RIGHT
        if j >= LEFT:
            # j's full centred window [j-LEFT, j+RIGHT] is
            # fully observed exactly at bar i == j + RIGHT.
            if h[j] >= np.max(h[j - LEFT:j + RIGHT + 1]):
                cur_high = j
            if l[j] <= np.min(l[j - LEFT:j + RIGHT + 1]):
                cur_low = j
        anchor_low[i] = cur_low
        anchor_high[i] = cur_high

    df["avwap_low"] = _avwap_series(tp, v, anchor_low)
    df["avwap_high"] = _avwap_series(tp, v, anchor_high)
    low = df["avwap_low"].to_numpy(dtype=float)
    high = df["avwap_high"].to_numpy(dtype=float)
    rising = np.zeros(n, dtype=bool)
    falling = np.zeros(n, dtype=bool)
    if n > RISE_BARS:
        rising[RISE_BARS:] = low[RISE_BARS:] > low[:-RISE_BARS]
        falling[RISE_BARS:] = high[RISE_BARS:] < high[:-RISE_BARS]
    df["avwap_low_rising"] = rising
    df["avwap_high_falling"] = falling
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
