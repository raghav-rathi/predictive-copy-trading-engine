"""Consecutive up/down days fade indicators (Larry Connors).

    up_streak   -- count of consecutive closes above the prior
                   close; resets to 0 on a down/flat close
    down_streak -- count of consecutive closes below the prior
                   close; resets to 0 on an up/flat close
    sma10       -- SMA(close, 10), the mean-reversion exit line

No lookahead: streaks count only closes through the current
bar; SMA is a causal rolling mean.
"""

import numpy as np
import pandas as pd

from strategies import base as B

STREAK_N = 4
SMA_N = 10


def add_indicators(
    df: pd.DataFrame,
    streak_n: int = STREAK_N,
    sma_n: int = SMA_N,
) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(float)
    n = len(df)
    up = np.zeros(n, dtype=int)
    down = np.zeros(n, dtype=int)
    for i in range(1, n):
        if c[i] > c[i - 1]:
            up[i] = up[i - 1] + 1
            down[i] = 0
        elif c[i] < c[i - 1]:
            down[i] = down[i - 1] + 1
            up[i] = 0
        else:  # flat close resets both streaks
            up[i] = 0
            down[i] = 0
    df["up_streak"] = up
    df["down_streak"] = down
    df["sma10"] = B.sma(df["c"], sma_n)
    return df
