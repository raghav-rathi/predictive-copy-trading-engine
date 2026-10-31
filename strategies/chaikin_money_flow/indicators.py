"""Chaikin Money Flow (20) indicators.

Formulas (Marc Chaikin):
    Money Flow Multiplier  MFM = ((C - L) - (H - C)) / (H - L),
                           with MFM = 0 when H == L (no range to locate
                           the close in; avoids division by zero).
    Money Flow Volume      MFV = MFM * V
    CMF(20) = sum(MFV, 20) / sum(V, 20),
              with CMF = 0 when the 20-bar volume sum is 0.

CMF is bounded in [-1, +1]: +1 means every bar in the window closed at
its high, -1 means every bar closed at its low. All windows use only
bars up to and including the current bar (strictly causal).

Columns:
    mfm, mfv -- per-bar multiplier and money flow volume
    cmf      -- Chaikin Money Flow (20)
    atr      -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h, l, c, v = df["h"], df["l"], df["c"], df["v"]
    rng = h - l
    mfm = np.where(rng != 0, ((c - l) - (h - c)) / rng.replace(0, np.nan), 0.0)
    df["mfm"] = pd.Series(mfm, index=df.index)
    df["mfv"] = df["mfm"] * v
    sum_mfv = df["mfv"].rolling(PERIOD, min_periods=PERIOD).sum()
    sum_v = v.rolling(PERIOD, min_periods=PERIOD).sum()
    df["cmf"] = np.where(sum_v != 0, sum_mfv / sum_v.replace(0, np.nan), 0.0)
    df["cmf"] = pd.Series(df["cmf"], index=df.index)
    df["atr"] = B.atr(h, l, c, 14)
    return df
