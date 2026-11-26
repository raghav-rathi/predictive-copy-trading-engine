"""The Strat bar classification + full-time-frame continuity (FTFC).

Rob Smith's The Strat classifies every bar against the prior
bar:

    1  = inside bar  (h <= prior h AND l >= prior l)
    2U = breaks the prior high only (h > prior h AND l >= prior l)
    2D = breaks the prior low only  (l < prior l AND h <= prior h)
    3  = outside bar (h > prior h AND l < prior l)

Equal highs/lows fall on the inside side of the boundary, so
the four classes partition every bar (a bar with h == prior h
and l == prior l is a 1). The class is stored as an int in
``strat_class``: 1, 2 (2U), -2 (2D), 3.

FTFC (full time frame continuity) gates direction: the daily
direction comes from 24-bar blocks and the weekly direction
from 168-bar blocks. A block's direction is the sign of its
last close minus its first open, and it is only applied to
bars AFTER the block completes (the block index is shifted
by one), so no lookahead. Bars before the first completed
block get direction 0 (neutral — no trade).

Columns:
    strat_class -- 1 / 2 / -2 / 3 per the table above
    ftfc_daily  -- +1 green / -1 red / 0 unknown, completed 24-bar blocks
    ftfc_weekly -- +1 green / -1 red / 0 unknown, completed 168-bar blocks
    atr14       -- ATR(14), diagnostic (the harness computes its own)

No lookahead: the class compares bar i only with bar i-1, and
the FTFC directions come from completed blocks only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

DAILY_BARS = 24
WEEKLY_BARS = 168


def _classify(h: pd.Series, l: pd.Series) -> pd.Series:
    prev_h = h.shift(1)
    prev_l = l.shift(1)
    breaks_high = h > prev_h
    breaks_low = l < prev_l
    out = pd.Series(np.ones(len(h), dtype=int), index=h.index)
    out = out.where(~(breaks_high & breaks_low), 3)   # 3: breaks both
    out = out.where(~(breaks_high & ~breaks_low), 2)  # 2U: high only
    out = out.where(~(~breaks_high & breaks_low), -2)  # 2D: low only
    # first bar has no prior bar: prev_h/prev_l are NaN, so both
    # comparisons are False and it stays a 1 (inside by default).
    return out


def _block_direction(o: pd.Series, c: pd.Series, block_bars: int) -> pd.Series:
    """Direction of each completed block, applied to later bars only.

    Returns a series aligned with the frame: +1 if the most
    recently COMPLETED block closed above its open, -1 if below,
    0 where no block has completed yet (or the block was flat).
    """
    n = len(o)
    idx = np.arange(n) // block_bars
    o_v = o.to_numpy()
    c_v = c.to_numpy()
    n_blocks = int(idx[-1]) + 1 if n else 0
    block_dir = np.zeros(n_blocks, dtype=int)
    for b in range(n_blocks):
        mask = idx == b
        first = np.argmax(mask)
        last = n - 1 - int(np.argmax(mask[::-1]))
        diff = c_v[last] - o_v[first]
        block_dir[b] = 1 if diff > 0 else (-1 if diff < 0 else 0)
    # bar i uses the direction of the block that completed before
    # its own block started: shift by one block.
    out = np.zeros(n, dtype=int)
    for i in range(n):
        b = idx[i]
        out[i] = block_dir[b - 1] if b >= 1 else 0
    return pd.Series(out, index=o.index)


def add_indicators(
    df: pd.DataFrame,
    daily_bars: int = DAILY_BARS,
    weekly_bars: int = WEEKLY_BARS,
) -> pd.DataFrame:
    df = df.copy()
    df["strat_class"] = _classify(df["h"], df["l"])
    df["ftfc_daily"] = _block_direction(df["o"], df["c"], daily_bars)
    df["ftfc_weekly"] = _block_direction(df["o"], df["c"], weekly_bars)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
