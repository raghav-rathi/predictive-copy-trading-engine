"""Fibonacci Fan indicators.

Fibonacci fan (rolling 50-bar leg): fan lines radiate from the window low through the 38.2% and 61.8% retracement points of the low-to-high leg, extended forward at the leg's slope. Long on close cross above the 38.2% fan line, short on cross below the 61.8% fan line; exits on the opposite cross. Redrawn each bar from data through that bar only — no repainting of past signals.
"""

import numpy as np
import pandas as pd

from strategies import base as B

WINDOW = 50


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    n = len(df)
    fan382 = np.full(n, np.nan)
    fan618 = np.full(n, np.nan)
    for i in range(WINDOW - 1, n):
        win_h = h[i - WINDOW + 1: i + 1]
        win_l = l[i - WINDOW + 1: i + 1]
        i_lo = int(np.argmin(win_l))
        i_hi = int(np.argmax(win_h))
        lo = win_l[i_lo]
        hi = win_h[i_hi]
        if i_hi <= i_lo or hi <= lo:
            continue
        span = hi - lo
        # fan lines pass through (i_lo, lo) and the retracement points
        # on the vertical through the high bar: hi - r*span
        for r, out in ((0.382, fan382), (0.618, fan618)):
            point = hi - r * span
            slope = (point - lo) / (i_hi - i_lo)
            out[i] = lo + slope * (WINDOW - 1 - i_lo)
    df["fan382"] = fan382
    df["fan618"] = fan618
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
