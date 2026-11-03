"""Fibonacci Pivots indicators.

Fibonacci pivot points on 1h bars: levels from the prior completed 24-bar block (pivot = (H+L+C)/3; R1 = P + 0.382*(H-L), S1 = P - 0.382*(H-L)). Long on close cross above R1, short on cross below S1; exits on cross back through the pivot. Levels are fixed within a block — no intraday repainting.
"""

import numpy as np
import pandas as pd

from strategies import base as B

BLOCK = 24


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    c = df["c"].to_numpy()
    n = len(df)
    pivot = np.full(n, np.nan)
    r1 = np.full(n, np.nan)
    s1 = np.full(n, np.nan)
    for i in range(BLOCK, n):
        block_start = (i // BLOCK) * BLOCK
        if block_start < BLOCK:
            continue
        ph = h[block_start - BLOCK: block_start].max()
        pl = l[block_start - BLOCK: block_start].min()
        pc = c[block_start - 1]
        p = (ph + pl + pc) / 3.0
        span = ph - pl
        pivot[i] = p
        r1[i] = p + 0.382 * span
        s1[i] = p - 0.382 * span
    df["pivot"] = pivot
    df["r1"] = r1
    df["s1"] = s1
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
