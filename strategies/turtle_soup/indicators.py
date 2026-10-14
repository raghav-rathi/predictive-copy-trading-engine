"""Turtle Soup + Plus One indicators (Linda Raschke, Street Smarts).

False-breakout fade: a signal bar makes a NEW 20-bar low where the prior
20-bar low level is at least 4 bars old (no fresh breakdowns mid-plunge).
The entry fires when, within the next 3 bars, price closes back above
that violated low -- the trapped-short squeeze. Mirror for highs.
No lookahead: extremes and ages use only bars through the current close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

N = 20
AGE_WINDOW = 40
AGE_MIN = 4
ENTRY_WINDOW = 3
ATR_N = 14


def _bars_ago_extreme(s: pd.Series, n: int, which: str) -> pd.Series:
    def f(y):
        i = int(np.argmax(y)) if which == "high" else int(np.argmin(y))
        return float(len(y) - 1 - i)

    return s.rolling(n, min_periods=N).apply(f, raw=True)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # extremes formed WITHOUT the current bar (breakout judged at close)
    df["prev_low20"] = df["l"].rolling(N, min_periods=N).min().shift(1)
    df["prev_high20"] = df["h"].rolling(N, min_periods=N).max().shift(1)
    new_low = (df["l"] < df["prev_low20"]).fillna(False)
    new_high = (df["h"] > df["prev_high20"]).fillna(False)
    low_age = _bars_ago_extreme(df["l"], AGE_WINDOW, "low").shift(1)
    high_age = _bars_ago_extreme(df["h"], AGE_WINDOW, "high").shift(1)
    df["sig_low_bar"] = (new_low & (low_age >= AGE_MIN)).fillna(False)
    df["sig_high_bar"] = (new_high & (high_age >= AGE_MIN)).fillna(False)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
