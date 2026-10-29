"""Kicker (kicking) pattern indicators (causal, no lookahead).

A kicker is a two-candle reversal (Steve Nison): the first candle
runs with the trend and the second gaps in the opposite direction
and closes strongly that way. The textbook gap test used here is
the CentralCharts/Nison kicking definition: the second candle's
open must be beyond the first candle's open, in the new direction.

    Bullish: bar i-1 black (c < o), bar i white (c > o),
             o[i] > o[i-1], and bar i's body is at least half its
             range (a strong, not doji-like, kicker candle).
    Bearish: mirror (bar i-1 white, bar i black, o[i] < o[i-1],
             |body[i]| >= 0.5 * range[i]).

The pattern completes on bar i, so it uses only bars i-1 and i.
No trend filter: Nison's kicking note (and the CentralCharts
reference) treats the preceding trend as of little importance
for this pattern, since the gap itself is the surprise.

Columns:
    kicker_dir -- +1 on a bullish kicker bar, -1 on a bearish
                  kicker bar, else 0
    atr        -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

MIN_BODY_FRAC = 0.5


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o = df["o"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    n = len(df)

    body = c - o
    rng = np.maximum(h - l, 0.0)
    strong = np.abs(body) >= MIN_BODY_FRAC * rng

    direction = np.zeros(n, dtype=int)
    if n >= 2:
        bull = (
            (c[:-1] < o[:-1])
            & (c[1:] > o[1:])
            & (o[1:] > o[:-1])
            & strong[1:]
        )
        bear = (
            (c[:-1] > o[:-1])
            & (c[1:] < o[1:])
            & (o[1:] < o[:-1])
            & strong[1:]
        )
        direction[np.where(bull)[0] + 1] = 1
        direction[np.where(bear)[0] + 1] = -1

    df["kicker_dir"] = direction
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
