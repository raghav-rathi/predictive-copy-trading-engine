"""DeMark Trendline Breakout indicators.

Tom DeMark TD trendlines: trendlines through the last two confirmed pivot highs (downtrend line) and last two confirmed pivot lows (uptrend line); pivots confirm with a 2-bar lag, so no lookahead. Long on close cross above the downtrend line, short on cross below the uptrend line; exits on the opposite cross.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    n = len(df)
    down_line = np.full(n, np.nan)
    up_line = np.full(n, np.nan)
    piv_highs: list[tuple[int, float]] = []
    piv_lows: list[tuple[int, float]] = []
    for i in range(n):
        # confirm pivot at j = i-2 using bars through i (2-bar lag, causal)
        j = i - 2
        if j >= 2:
            if h[j] >= h[j - 1] and h[j] >= h[j - 2] and h[j] > h[j + 1] and h[j] > h[j + 2]:
                piv_highs.append((j, h[j]))
            if l[j] <= l[j - 1] and l[j] <= l[j - 2] and l[j] < l[j + 1] and l[j] < l[j + 2]:
                piv_lows.append((j, l[j]))
        if len(piv_highs) >= 2:
            (b1, p1), (b2, p2) = piv_highs[-2], piv_highs[-1]
            if b2 > b1:
                slope = (p2 - p1) / (b2 - b1)
                down_line[i] = p2 + slope * (i - b2)
        if len(piv_lows) >= 2:
            (b1, p1), (b2, p2) = piv_lows[-2], piv_lows[-1]
            if b2 > b1:
                slope = (p2 - p1) / (b2 - b1)
                up_line[i] = p2 + slope * (i - b2)
    df["downtrend_line"] = down_line
    df["uptrend_line"] = up_line
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
