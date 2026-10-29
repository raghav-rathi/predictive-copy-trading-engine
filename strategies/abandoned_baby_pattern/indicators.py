"""Abandoned baby candle pattern indicators (Steve Nison).

A 3-bar reversal, all gaps strict (no overlap allowed):

Bullish abandoned baby (bars i-2, i-1, i):
  - bar i-2: long black candle (bearish, body >= 40% of range)
  - bar i-1: doji (body <= 10% of range) gapping DOWN:
    doji high < bar i-2 low
  - bar i: long white candle (bullish, body >= 40% of range)
    gapping UP: bar i low > doji high, close above the
    midpoint of bar i-2, and volume >= the prior 20-bar
    average volume (confirmation that the reversal is backed
    by participation).

Bearish abandoned baby mirrors all of the above.

Detection uses only bars through i, so the signal bar is the
third candle's close -- causal. Columns: ab_dir (+1 bullish
baby, -1 bearish baby, else 0), vol_sma20 (prior-bar average
volume), atr.
"""

import numpy as np
import pandas as pd

from strategies import base as B

DOJI_MAX_BODY_FRAC = 0.10
LONG_BODY_MIN_FRAC = 0.40
VOL_N = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    o = df["o"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)

    rng = h - l
    body = np.abs(c - o)
    with np.errstate(invalid="ignore", divide="ignore"):
        body_frac = np.where(rng > 0, body / np.where(rng > 0, rng, 1.0), 0.0)
    is_doji = (body_frac <= DOJI_MAX_BODY_FRAC) & (rng > 0)
    is_long_body = body_frac >= LONG_BODY_MIN_FRAC

    vol_avg = pd.Series(v).rolling(VOL_N, min_periods=VOL_N).mean().shift(1).to_numpy(dtype=float)

    direction = np.zeros(n, dtype=int)
    for i in range(2, n):
        if not np.isfinite(vol_avg[i]) or v[i] < vol_avg[i]:
            continue
        # bullish: black, doji gap-down, white gap-up
        if (
            c[i - 2] < o[i - 2] and is_long_body[i - 2]
            and is_doji[i - 1] and h[i - 1] < l[i - 2]
            and c[i] > o[i] and is_long_body[i]
            and l[i] > h[i - 1]
            and c[i] > (o[i - 2] + c[i - 2]) / 2
        ):
            direction[i] = 1
        # bearish: white, doji gap-up, black gap-down
        elif (
            c[i - 2] > o[i - 2] and is_long_body[i - 2]
            and is_doji[i - 1] and l[i - 1] > h[i - 2]
            and c[i] < o[i] and is_long_body[i]
            and h[i] < l[i - 1]
            and c[i] < (o[i - 2] + c[i - 2]) / 2
        ):
            direction[i] = -1

    df["ab_dir"] = direction
    df["vol_sma20"] = vol_avg
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
