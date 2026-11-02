"""Gann fan indicators (W.D. Gann's angle lines).

The 1x1 fan line rises from the 30-bar swing low at one ATR(14)
per bar and falls from the 30-bar swing high at the same rate.
Anchors are the rolling 30-bar extremes, recomputed each bar, so
the lines are causal: the anchor for bar i uses only bars up to i.

Columns:
    fan_up, fan_down, atr
"""

import numpy as np
import pandas as pd

from strategies import base as B

WINDOW = 30


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    atr_v = B.atr(df["h"], df["l"], df["c"], 14).to_numpy()
    n = len(df)
    fan_up = np.full(n, np.nan)
    fan_down = np.full(n, np.nan)
    for i in range(n):
        s = max(0, i - WINDOW + 1)
        w_h = h[s:i + 1]
        w_l = l[s:i + 1]
        hi_idx = s + int(np.argmax(w_h))
        lo_idx = s + int(np.argmin(w_l))
        if not np.isnan(atr_v[i]):
            fan_up[i] = w_l.min() + atr_v[i] * (i - lo_idx)
            fan_down[i] = w_h.max() - atr_v[i] * (i - hi_idx)
    df["fan_up"] = fan_up
    df["fan_down"] = fan_down
    df["atr"] = atr_v
    return df
