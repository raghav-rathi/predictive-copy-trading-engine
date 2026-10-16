"""Raschke "Tail" pattern indicators.

A Tail is a bar with a long protruding wick that also marks a fresh
20-bar extreme: a bullish tail has a long lower wick and prints the
20-bar low; a bearish tail has a long upper wick and prints the 20-bar
high. The bar's range must clear 0.75x ATR(14) to reject doji noise.
"""

import pandas as pd

from strategies import base as B


def add_indicators(
    df: pd.DataFrame,
    tail_n: int = 20,
    wick_mult: float = 2.0,
    wick_range_frac: float = 0.5,
    min_range_atr: float = 0.75,
    atr_n: int = 14,
) -> pd.DataFrame:
    df = df.copy()
    o, h, l, c = df["o"], df["h"], df["l"], df["c"]
    rng = h - l
    body = (c - o).abs()
    body_max = pd.concat([o, c], axis=1).max(axis=1)
    body_min = pd.concat([o, c], axis=1).min(axis=1)
    lower_wick = body_min - l
    upper_wick = h - body_max
    atr = B.atr(h, l, c, atr_n)
    roll_min = l.rolling(tail_n, min_periods=tail_n).min()
    roll_max = h.rolling(tail_n, min_periods=tail_n).max()

    df["atr14"] = atr
    df["bullish_tail"] = (
        (lower_wick >= wick_mult * body)
        & (lower_wick >= wick_range_frac * rng)
        & ((l - roll_min).abs() <= 1e-9)
        & (rng >= min_range_atr * atr)
    ).fillna(False).astype(bool)
    df["bearish_tail"] = (
        (upper_wick >= wick_mult * body)
        & (upper_wick >= wick_range_frac * rng)
        & ((h - roll_max).abs() <= 1e-9)
        & (rng >= min_range_atr * atr)
    ).fillna(False).astype(bool)
    return df
