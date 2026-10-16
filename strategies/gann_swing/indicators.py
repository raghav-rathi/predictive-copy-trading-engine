"""Gann swing chart indicators (1-bar minor swing + 3-bar main swing),
implemented in my own words from the documented swing-chart method.

1-bar (minor) swing direction, causal left-to-right:
  up   if h[i] > h[i-1] and l[i] > l[i-1]
  down if h[i] < h[i-1] and l[i] < l[i-1]
  else carry the prior direction (inside/outside bars hold the swing).

3-bar (main) trend, causal left-to-right:
  flips up   when h[i] > max(h[i-1], h[i-2], h[i-3])   (3-bar high break)
  flips down when l[i] < min(l[i-1], l[i-2], l[i-3])   (3-bar low break)
  else carry the prior trend (an outside bar breaking both keeps the
  prior trend — indecision, not a flip).

TREND_BARS is the sweep knob (default 3); calibration compares 2/3/4.
"""

import numpy as np
import pandas as pd

TREND_BARS = 3


def _swing_direction(h: pd.Series, l: pd.Series) -> np.ndarray:
    hv, lv = h.to_numpy(dtype=float), l.to_numpy(dtype=float)
    n = len(hv)
    d = np.zeros(n, dtype=int)
    cur = 0
    for i in range(1, n):
        up = hv[i] > hv[i - 1] and lv[i] > lv[i - 1]
        dn = hv[i] < hv[i - 1] and lv[i] < lv[i - 1]
        if up and not dn:
            cur = 1
        elif dn and not up:
            cur = -1
        d[i] = cur
    return d


def _main_trend(h: pd.Series, l: pd.Series, bars: int | None = None) -> np.ndarray:
    if bars is None:
        bars = TREND_BARS  # read at call time so calibration can override
    hv, lv = h.to_numpy(dtype=float), l.to_numpy(dtype=float)
    n = len(hv)
    t = np.zeros(n, dtype=int)
    cur = 0
    for i in range(bars, n):
        hi_break = hv[i] > max(hv[i - b] for b in range(1, bars + 1))
        lo_break = lv[i] < min(lv[i - b] for b in range(1, bars + 1))
        if hi_break and not lo_break:
            cur = 1
        elif lo_break and not hi_break:
            cur = -1
        t[i] = cur
    return t


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["gann_swing1"] = _swing_direction(df["h"], df["l"])
    df["gann_trend3"] = _main_trend(df["h"], df["l"])
    return df
