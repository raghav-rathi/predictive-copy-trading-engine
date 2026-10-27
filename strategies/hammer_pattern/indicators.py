"""Nison hammer / shooting star detector.

Hammer (bullish reversal): prior 3-bar downtrend (close below the
close 3 bars earlier), body in the upper third of the range, lower
shadow >= 2x body, upper shadow <= body. Shooting star is the
mirror. This is stricter than pin_bar_reversal (which only needs a
2/3 tail at a 5-bar extreme): the hammer also requires the trend
context and the body-position rule. Columns: hammer (+1), star
(-1), pattern (+1/-1/0), atr.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o, h, l, c = df["o"], df["h"], df["l"], df["c"]
    body = (c - o).abs()
    rng = h - l
    lower = np.minimum(o, c) - l
    upper = h - np.maximum(o, c)
    downtrend = c.shift(1) < c.shift(4)
    uptrend = c.shift(1) > c.shift(4)
    hammer = (
        downtrend
        & (lower >= 2 * body)
        & (upper <= body)
        & (np.minimum(o, c) >= l + (2.0 / 3.0) * rng)
        & (body > 0)
    )
    star = (
        uptrend
        & (upper >= 2 * body)
        & (lower <= body)
        & (np.maximum(o, c) <= l + (1.0 / 3.0) * rng)
        & (body > 0)
    )
    pat = np.where(hammer, 1, np.where(star, -1, 0))
    df["hammer"] = hammer.fillna(False).astype(int)
    df["star"] = star.fillna(False).astype(int)
    df["pattern"] = pat
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
