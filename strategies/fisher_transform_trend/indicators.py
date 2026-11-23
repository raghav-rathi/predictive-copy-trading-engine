"""Ehlers Fisher Transform indicators (causal, no lookahead).

John Ehlers, "The Fisher Transform" (Mesa Software / Cybernetic
Analysis for Stocks and Futures, 2004). Pipeline, computed bar by
bar using only data through bar i:

1. Normalize the close inside the trailing 10-bar high/low range:
       raw = (C - min(L, 10)) / (max(H, 10) - min(L, 10))
   raw lies in [0, 1] by construction.
2. Map to [-1, 1]: x = 2 * raw - 1, clamped to +/-0.999 so the
   logarithm below stays finite.
3. Fisher-transform: fisher_raw = 0.5 * ln((1 + x) / (1 - x)).
4. Smooth once: fisher[i] = 0.5 * fisher_raw[i] + 0.5 * fisher[i-1].

Seeding (deterministic, no NaN leaks): before the first complete
10-bar window (bars 0..8) fisher_raw is defined as 0.0, i.e. the
price is treated as sitting at the middle of its (as yet unknown)
range, so x = 0 and fisher_raw = 0. Bars with a zero 10-bar range
(hi == lo, e.g. a perfectly flat stretch) also get raw = 0.5, i.e.
x = 0. The recursion is seeded fisher = 0.0 at bar 0. WARMUP = 30
bars is far longer than the 10-bar window plus the smoothing
settle, so the seed has no effect on traded bars.

Columns:
    x_norm      -- normalized price position mapped to [-1, 1]
    fisher_raw  -- unsmoothed Fisher transform of x_norm
    fisher      -- smoothed Fisher transform (the traded series)
    atr         -- Wilder ATR(14) for the risk layer

No lookahead: every value at bar i uses highs/lows/closes through
bar i only, and the recursion uses only its own prior value.
"""

import numpy as np
import pandas as pd

N = 10
CLIP = 0.999
SMOOTH = 0.5


def fisher_transform(c, h, l, n: int = N):
    """Return (x_norm, fisher_raw, fisher) series for OHLCV data.

    Pure function of the three series; deterministic seeding as
    documented in the module docstring.
    """
    lo = l.rolling(n, min_periods=n).min()
    hi = h.rolling(n, min_periods=n).max()
    rng = hi - lo
    raw = ((c - lo) / rng).where(rng > 0, 0.5)
    raw = raw.fillna(0.5)
    x = (2.0 * raw - 1.0).clip(-CLIP, CLIP)
    with np.errstate(divide="ignore", invalid="ignore"):
        fisher_raw = 0.5 * np.log((1.0 + x) / (1.0 - x))
    fisher_raw = fisher_raw.replace([np.inf, -np.inf], 0.0).fillna(0.0)
    # Recursive 0.5/0.5 smoothing, seeded at 0.0.
    fr = fisher_raw.to_numpy(dtype=float)
    fisher = np.zeros(len(fr))
    prev = 0.0
    for i in range(len(fr)):
        prev = SMOOTH * fr[i] + (1.0 - SMOOTH) * prev
        fisher[i] = prev
    return (
        pd.Series(x.to_numpy(), index=c.index, name="x_norm"),
        pd.Series(fr, index=c.index, name="fisher_raw"),
        pd.Series(fisher, index=c.index, name="fisher"),
    )


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    from strategies import base as B

    df = df.copy()
    x, fisher_raw, fisher = fisher_transform(df["c"], df["h"], df["l"])
    df["x_norm"] = x
    df["fisher_raw"] = fisher_raw
    df["fisher"] = fisher
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
