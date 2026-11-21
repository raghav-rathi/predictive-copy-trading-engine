"""On-Balance Volume Breakout indicators.

OBV (Joseph Granville): OBV[0] = 0; OBV[i] = OBV[i-1] + v[i] if
c[i] > c[i-1], OBV[i-1] - v[i] if c[i] < c[i-1], unchanged if the
close is equal. The breakout levels are the highest / lowest OBV
of the PRIOR 20 bars (bars i-20..i-1), trailing and shifted by one
bar.

Columns:
    obv -- cumulative On-Balance Volume
    obv_high / obv_low -- prior-20-bar high / low of OBV
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only; the breakout levels use bars i-20..i-1.
"""

import numpy as np
import pandas as pd

from strategies import base as B

LOOK_N = 20
ATR_N = 14


def add_indicators(df: pd.DataFrame, look_n: int = LOOK_N,
                   atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    v = df["v"]
    delta = c.diff()
    contrib = pd.Series(
        np.where(delta > 0, v, np.where(delta < 0, -v, 0.0)),
        index=df.index,
    )
    df["obv"] = contrib.cumsum()
    df["obv_high"] = df["obv"].rolling(look_n, min_periods=look_n).max().shift(1)
    df["obv_low"] = df["obv"].rolling(look_n, min_periods=look_n).min().shift(1)
    df["atr"] = B.atr(df["h"], df["l"], c, atr_n)
    return df
