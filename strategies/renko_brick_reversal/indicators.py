"""Renko brick construction from 1h closes (classic Renko charting).

Classic Renko (Japanese "renga", brick) ignores time: a new brick
prints only when price moves a fixed brick size beyond the last
brick's edge. True Renko is built from tick closes; here the 1h
close is used as the price feed, so this is a close-based
approximation of tick Renko -- intrabar excursions that never
close beyond a brick edge are invisible, and a brick can only print
once per 1h bar at most in count terms (in fact several bricks can
print on one bar if the close jumps more than one brick size).

    brick_size = mean ATR(14) over the first 200 bars, fixed per coin
    anchor     = close[0]; last brick spans [last_bottom, last_top]
    +1 brick   = close >= last_top + brick_size   (top += brick_size)
    -1 brick   = close <= last_bottom - brick_size (bottom -= brick_size)

A reversal needs two brick sizes against the last brick, which is
the classic Renko reversal rule (to flip direction price must
travel 2x the brick from the last brick's far edge).

Columns:

    brick_size   -- fixed per-coin brick size (ATR(14) mean, first 200 bars)
    renko_dir    -- direction of the last brick (+1 / -1, 0 before any brick)
    renko_run    -- consecutive bricks in the current direction
    renko_prev_run -- length of the run immediately before the current one
    renko_top / renko_bottom -- edges of the last brick
    renko_bricks -- cumulative brick count
    atr          -- Wilder ATR(14) for the risk layer

No lookahead: the brick size uses only the first 200 bars (inside the
220-bar warmup), and every brick on bar i uses closes through bar i.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_N = 14
BRICK_BARS = 200  # bars used to fix the brick size (mean ATR(14))
WARMUP = 220


def brick_size_from(df: pd.DataFrame, n_bars: int = BRICK_BARS) -> float:
    """Fixed brick size: mean ATR(14) over the first ``n_bars`` bars."""
    a = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return float(a.iloc[ATR_N - 1:n_bars].mean())


def renko_bricks(c: pd.Series, brick: float) -> pd.DataFrame:
    """Build the brick sequence bar by bar from closes.

    Returns per-bar state: direction of the last brick, current run
    length, previous run length, last brick edges, brick count.
    """
    closes = c.to_numpy(dtype=float)
    n = len(closes)
    direction = np.zeros(n, dtype=int)
    run = np.zeros(n, dtype=int)
    prev_run = np.zeros(n, dtype=int)
    top = np.full(n, np.nan)
    bottom = np.full(n, np.nan)
    count = np.zeros(n, dtype=int)

    last_top = closes[0]
    last_bottom = closes[0]
    cur_dir = 0
    cur_run = 0
    last_run = 0
    total = 0

    for i in range(n):
        px = closes[i]
        # keep adding bricks while the close clears the next edge
        while px >= last_top + brick:
            if cur_dir == 1:
                cur_run += 1
            else:
                last_run = cur_run
                cur_dir = 1
                cur_run = 1
            last_top += brick
            last_bottom = last_top - brick
            total += 1
        while px <= last_bottom - brick:
            if cur_dir == -1:
                cur_run += 1
            else:
                last_run = cur_run
                cur_dir = -1
                cur_run = 1
            last_bottom -= brick
            last_top = last_bottom + brick
            total += 1
        direction[i] = cur_dir
        run[i] = cur_run
        prev_run[i] = last_run
        top[i] = last_top
        bottom[i] = last_bottom
        count[i] = total

    return pd.DataFrame(
        {
            "renko_dir": direction,
            "renko_run": run,
            "renko_prev_run": prev_run,
            "renko_top": top,
            "renko_bottom": bottom,
            "renko_bricks": count,
        },
        index=c.index,
    )


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    brick = brick_size_from(df)
    rb = renko_bricks(df["c"], brick)
    df["brick_size"] = brick
    df["renko_dir"] = rb["renko_dir"]
    df["renko_run"] = rb["renko_run"]
    df["renko_prev_run"] = rb["renko_prev_run"]
    df["renko_top"] = rb["renko_top"]
    df["renko_bottom"] = rb["renko_bottom"]
    df["renko_bricks"] = rb["renko_bricks"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
