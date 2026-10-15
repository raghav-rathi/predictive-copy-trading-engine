"""Renko brick-trend indicators.

Renko bricks of size 0.5 * ATR(14), built causally from closes: a new
brick is added whenever price moves at least one brick from the last
brick edge; a reversal needs a single brick in the opposite direction
(standard renko, not the 3-box variant). Time is ignored — only price
movement counts, which is the whole point of renko: noise filtering.

  renko_dir: +1 in an up-brick run, -1 in a down-brick run, 0 before
             the first brick completes.
No lookahead: brick state at bar i depends only on closes through i.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_N = 14
BRICK_ATR_MULT = 0.5


def _renko_direction(closes: np.ndarray, brick: np.ndarray) -> np.ndarray:
    n = len(closes)
    out = np.zeros(n, dtype=int)
    started = False
    level = 0.0
    cur = 0
    for i in range(n):
        b = brick[i]
        px = closes[i]
        if np.isnan(b) or b <= 0 or np.isnan(px):
            out[i] = cur
            continue
        if not started:
            level, started = px, True
            out[i] = cur
            continue
        while px >= level + b:
            level += b
            cur = 1
        while px <= level - b:
            level -= b
            cur = -1
        out[i] = cur
    return out


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    atr = B.atr(df["h"], df["l"], df["c"], ATR_N)
    brick = atr * BRICK_ATR_MULT
    df["brick"] = brick
    df["renko_dir"] = _renko_direction(
        df["c"].to_numpy(dtype=float), brick.to_numpy(dtype=float)
    )
    return df
