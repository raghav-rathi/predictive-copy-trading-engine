"""Pin bar / Pinocchio bar rejection (Martin Pring's price-action canon).

A pin bar is a single candle with a long rejection tail and a small
real body: the market probed far in one direction and was rejected
back.  With

    rng        = h - l                      (guard: rng > 0)
    body       = abs(c - o)
    upper_wick = h - max(o, c)
    lower_wick = min(o, c) - l

    bullish_pin = (lower_wick >= 2/3*rng) & (body <= 1/3*rng) &
                  (upper_wick <= 0.2*rng) & (l == rolling_min(l, 5))
    bearish_pin = (upper_wick >= 2/3*rng) & (body <= 1/3*rng) &
                  (lower_wick <= 0.2*rng) & (h == rolling_max(h, 5))

The 2/3-tail / 1/3-body / 0.2-opposite-wick cutoffs are fixed a
priori (the canonical textbook shape); the 5-bar swing location
filter is the Pring rule that the rejection must occur at a local
extreme — a long tail in the middle of nowhere is just noise.  No
lookahead: the rolling min/max at bar i use data through bar i only
(min_periods=5, so the first 4 bars can never be pins).

Columns added:
    rng, body, upper_wick, lower_wick, bullish_pin, bearish_pin, atr
"""

import numpy as np
import pandas as pd

from strategies import base as B

TAIL_FRAC = 2.0 / 3.0   # rejection tail must dominate the bar
BODY_FRAC = 1.0 / 3.0   # real body must be small
WICK_FRAC = 0.2         # opposite wick must be tiny
SWING_N = 5             # swing location filter length


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o = df["o"].astype(float)
    h = df["h"].astype(float)
    l = df["l"].astype(float)
    c = df["c"].astype(float)

    rng = h - l
    body = (c - o).abs()
    upper_wick = h - np.maximum(o, c)
    lower_wick = np.minimum(o, c) - l
    valid = rng > 0  # flat bars (doji of zero range) are never pins

    shape_bull = (
        (lower_wick >= TAIL_FRAC * rng)
        & (body <= BODY_FRAC * rng)
        & (upper_wick <= WICK_FRAC * rng)
    )
    shape_bear = (
        (upper_wick >= TAIL_FRAC * rng)
        & (body <= BODY_FRAC * rng)
        & (lower_wick <= WICK_FRAC * rng)
    )
    swing_low = l.rolling(SWING_N, min_periods=SWING_N).min()
    swing_high = h.rolling(SWING_N, min_periods=SWING_N).max()

    df["rng"] = rng
    df["body"] = body
    df["upper_wick"] = upper_wick
    df["lower_wick"] = lower_wick
    df["bullish_pin"] = (
        (shape_bull & valid & (l == swing_low)).fillna(False).astype(bool)
    )
    df["bearish_pin"] = (
        (shape_bear & valid & (h == swing_high)).fillna(False).astype(bool)
    )
    df["atr"] = B.atr(h, l, c, 14)
    return df
