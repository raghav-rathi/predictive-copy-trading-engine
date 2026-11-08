"""Fast stochastic %K/%D crossover indicators.

Fast %K(14) = 100 x (close - LL14) / (HH14 - LL14) over the trailing
14 bars including the current bar; %D = SMA(3) of %K. A zero range
(HH14 == LL14, e.g. flat data) maps to %K = 50. SMA(200) is the
trend filter for the entry rules.
"""

import numpy as np
import pandas as pd

from strategies.base import sma

K_WINDOW = 14
D_WINDOW = 3

INDICATOR_COLS = [
    "stoch_k",
    "stoch_d",
    "sma200",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"]
    l = df["l"]
    c = df["c"]
    ll = l.rolling(K_WINDOW, min_periods=K_WINDOW).min()
    hh = h.rolling(K_WINDOW, min_periods=K_WINDOW).max()
    rng = hh - ll
    k = 100.0 * (c - ll) / rng
    k = k.where(rng > 0, 50.0)
    df["stoch_k"] = k
    df["stoch_d"] = k.rolling(D_WINDOW, min_periods=D_WINDOW).mean()
    df["sma200"] = sma(c, 200)
    return df
