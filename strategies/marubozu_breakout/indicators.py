"""Marubozu detector: body >= 90% of the bar's range.

A marubozu has (almost) no shadows: buyers (sellers) controlled
the whole bar. The signal is the candle itself, not a pattern
context — that is the point of the marubozu in Nison's canon, and
also its weakness on 1h bars, where full-body bars are common.
Columns: marubozu_dir (+1/-1/0), atr.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    body = (df["c"] - df["o"]).abs()
    rng = df["h"] - df["l"]
    strong = (rng > 0) & (body >= 0.90 * rng)
    bull = strong & (df["c"] > df["o"])
    bear = strong & (df["c"] < df["o"])
    df["marubozu_dir"] = np.where(bull, 1, np.where(bear, -1, 0))
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
