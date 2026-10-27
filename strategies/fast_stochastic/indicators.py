"""Lane Fast Stochastic: %K(14) with a 3-bar SMA %D signal line.

Fast %K uses no smoothing of its own (that is the whole difference
from slow_stochastic, which smooths %K first): %K = 100 * (C - LL14) /
(HH14 - LL14); %D = SMA(3) of %K. Columns: stoch_k, stoch_d, atr.
"""

import numpy as np
import pandas as pd

from strategies import base as B

N = 14
D = 3


def add_indicators(df: pd.DataFrame, n: int = N, d: int = D) -> pd.DataFrame:
    df = df.copy()
    ll = df["l"].rolling(n, min_periods=n).min()
    hh = df["h"].rolling(n, min_periods=n).max()
    rng = (hh - ll).replace(0, np.nan)
    k = 100 * (df["c"] - ll) / rng
    df["stoch_k"] = k
    df["stoch_d"] = k.rolling(d, min_periods=d).mean()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
