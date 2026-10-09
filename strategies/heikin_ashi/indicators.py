"""Heikin-Ashi trend indicators (Dan Valcu, six rules).

haClose = (o+h+l+c)/4; haOpen = (prev haOpen + prev haClose)/2 (seeded
from the first bar's open); haHigh = max(h, haOpen, haClose);
haLow = min(l, haOpen, haClose). Consolidation bar =
|haClose-haOpen| < 0.25 x (haHigh-haLow). Computed sequentially from the
first bar, so trivially no-lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CONSOL_BODY_FRAC = 0.25
ATR_N = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o = df["o"].to_numpy()
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    c = df["c"].to_numpy()
    n = len(df)
    haC = (o + h + l + c) / 4
    haO = np.empty(n)
    haO[0] = o[0]
    for i in range(1, n):
        haO[i] = (haO[i - 1] + haC[i - 1]) / 2
    haH = np.maximum(np.maximum(h, haO), haC)
    haL = np.minimum(np.minimum(l, haO), haC)
    df["ha_open"] = haO
    df["ha_close"] = haC
    df["ha_high"] = haH
    df["ha_low"] = haL
    body = np.abs(haC - haO)
    rng = haH - haL
    df["ha_consol"] = pd.Series((body < CONSOL_BODY_FRAC * rng), index=df.index).fillna(False)
    df["ha_green"] = pd.Series(haC > haO, index=df.index)
    df["ha_red"] = pd.Series(haC < haO, index=df.index)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
