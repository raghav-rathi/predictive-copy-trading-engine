"""Cup and Handle entry signals (bullish only -- O'Neil's pattern).

Evaluated at each bar j (needs >= 301 bars of history). The cup and
handle must be fully formed by bar j-1; bar j is the breakout bar:

  left rim : highest high in [j-301, j-1]         -> (rim_idx, rim_px)
  bottom   : lowest low in [rim_idx, j]            -> (bot_idx, bot_px)
  cup      : 60 <= j - rim_idx <= 300 bars
             8% <= (rim_px - bot_px)/rim_px <= 25%        (cup depth)
             1xATR <= rim_px - bot_px <= 4xATR           (volatility band)
  right rim: highest high in [bot_idx, j] within 5% of the left rim
  handle   : pullback after the right rim --
             duration <= cup_duration/3,
             handle low in the upper half of the cup
                 (handle_low >= (rim_px + bot_px)/2),
             handle depth <= cup depth / 3
  long_entry: close above the handle high AND volume > 1.4x the
      20-bar average volume.

Short side: the pattern is a bullish continuation by construction, so
short_entry/short_exit are all False (allow_shorts=False in risk.py).
Exits are the harness 1.5xATR stop / 4.0xATR target (cup-depth
projection proxy) / 120-bar max hold; long_exit is structurally False
(the pattern has no defined failure exit beyond the stop).

No lookahead: every extremum is drawn from bars <= j, the entry uses
bar j's close and volume, and the harness executes at bar j+1's open.
"""

import numpy as np
import pandas as pd

LOOKBACK = 300
CUP_MIN_BARS = 60
CUP_DEPTH_MIN = 0.08
CUP_DEPTH_MAX = 0.25
RIM_TOL = 0.05
VOL_MULT = 1.4


def _detect(df: pd.DataFrame) -> np.ndarray:
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)
    uptrend = df["uptrend"].to_numpy(dtype=bool)
    vol_avg = df["vol_avg20"].to_numpy(dtype=float)
    atr = df["atr"].to_numpy(dtype=float)
    n = len(df)
    entry = np.zeros(n, dtype=bool)

    for j in range(LOOKBACK + 1, n):
        if not uptrend[j]:
            continue
        a = float(atr[j])
        if not np.isfinite(a) or a <= 0:
            continue
        # the pattern (cup + handle) must be complete by bar e = j - 1;
        # bar j is the breakout bar
        e = j - 1
        lo = e - LOOKBACK
        # left rim: highest high in the lookback window
        rim_rel = int(np.argmax(h[lo: e + 1]))
        rim_idx = lo + rim_rel
        rim_px = h[rim_idx]
        # bottom: lowest low after the left rim
        seg_l = l[rim_idx: e + 1]
        bot_rel = int(np.argmin(seg_l))
        bot_idx = rim_idx + bot_rel
        bot_px = l[bot_idx]
        cup_dur = e - rim_idx
        if cup_dur < CUP_MIN_BARS:
            continue
        cup_depth = rim_px - bot_px
        if cup_depth <= 0:
            continue
        if not (CUP_DEPTH_MIN <= cup_depth / rim_px <= CUP_DEPTH_MAX):
            continue
        if not (a <= cup_depth <= 4 * a):
            continue
        # right rim: highest high after the bottom, within 5% of left rim
        seg_h = h[bot_idx: e + 1]
        rrim_rel = int(np.argmax(seg_h))
        rrim_idx = bot_idx + rrim_rel
        rrim_px = h[rrim_idx]
        if rrim_px < (1 - RIM_TOL) * rim_px:
            continue
        # handle: pullback after the right rim
        handle_dur = e - rrim_idx
        if handle_dur < 1 or handle_dur > cup_dur / 3:
            continue
        hseg_h = h[rrim_idx: e + 1]
        hseg_l = l[rrim_idx: e + 1]
        handle_high = hseg_h.max()
        handle_low = hseg_l.min()
        if handle_low < (rim_px + bot_px) / 2:   # must hold the upper half
            continue
        if (handle_high - handle_low) > cup_depth / 3:  # shallow handle
            continue
        # breakout: close through the handle high on expanding volume
        va = vol_avg[j]
        if not np.isfinite(va) or va <= 0:
            continue
        if c[j] > handle_high and v[j] > VOL_MULT * va:
            entry[j] = True
    return entry


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry = _detect(df)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = np.zeros(len(df), dtype=bool)
    df["long_exit"] = np.zeros(len(df), dtype=bool)
    df["short_exit"] = np.zeros(len(df), dtype=bool)
    return df
