"""Percentage moving-average envelope — SMA(20) plus/minus 5%.

Unlike ATR or standard-deviation bands, the envelope is a fixed
percentage: the market is "over-extended" only relative to its own
recent average, not to its volatility. A close outside the envelope
is traded as a breakout (not a fade — the library already has
mean-reversion variants; this one tests the breakout reading).

Columns:
    env_mid   -- SMA(20) of close
    env_upper -- mid * 1.05
    env_lower -- mid * 0.95
    atr       -- Wilder ATR(14) for the risk layer

No lookahead: SMA is a trailing window.
"""

import numpy as np
import pandas as pd

from strategies import base as B

MID_N = 20
PCT = 0.05


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    mid = B.sma(df["c"], MID_N)
    df["env_mid"] = mid
    df["env_upper"] = mid * (1.0 + PCT)
    df["env_lower"] = mid * (1.0 - PCT)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
