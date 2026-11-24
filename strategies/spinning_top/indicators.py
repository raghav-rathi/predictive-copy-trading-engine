"""Spinning top indicators (Steve Nison).

Per bar:

    rng        = h - l
    body       = |c - o|
    upper_wick = h - max(o, c)
    lower_wick = min(o, c) - l

A spinning top is a small body with long wicks on both sides —
indecision: price probed both directions and closed near where
it opened:

    body <= 0.30 * rng AND upper_wick >= 0.30 * rng
    AND lower_wick >= 0.30 * rng (and rng > 0, so a flat bar
    cannot qualify).

The swing context is the prior 20 bars excluding the current
bar (shifted, so the current bar's own extreme cannot qualify
itself): swing_low is the lowest low of the prior 20 bars,
swing_high the highest high of the prior 20 bars. A spinning
top whose low reaches the prior 20-bar low sits at a swing
low; one whose high reaches the prior 20-bar high sits at a
swing high.

Columns:
    rng, body, upper_wick, lower_wick -- candle anatomy
    is_spinning_top -- the pattern flag
    swing_low, swing_high -- prior-20-bar extremes (excl. current bar)

No lookahead: every value on bar j uses data through bar j's
close only (the swing windows are shifted by one bar).
"""

import pandas as pd

SWING_LOOKBACK = 20  # shipped default
BODY_MAX = 0.30       # body at most 30% of the range
WICK_MIN = 0.30       # each wick at least 30% of the range


def add_indicators(
    df: pd.DataFrame,
    swing_lookback: int = SWING_LOOKBACK,
    body_max: float = BODY_MAX,
    wick_min: float = WICK_MIN,
) -> pd.DataFrame:
    df = df.copy()
    df["rng"] = df["h"] - df["l"]
    df["body"] = (df["c"] - df["o"]).abs()
    df["upper_wick"] = df["h"] - df[["o", "c"]].max(axis=1)
    df["lower_wick"] = df[["o", "c"]].min(axis=1) - df["l"]
    df["is_spinning_top"] = (
        (df["rng"] > 0)
        & (df["body"] <= body_max * df["rng"])
        & (df["upper_wick"] >= wick_min * df["rng"])
        & (df["lower_wick"] >= wick_min * df["rng"])
    )
    df["swing_low"] = (
        df["l"].rolling(swing_lookback, min_periods=swing_lookback).min().shift(1)
    )
    df["swing_high"] = (
        df["h"].rolling(swing_lookback, min_periods=swing_lookback).max().shift(1)
    )
    return df
