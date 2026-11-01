"""Negative Volume Index indicators (Dysart / Fosback).

Premise: smart money is active on low-volume days, so only price
changes on decreasing-volume bars move the index; increasing-volume
bars leave it unchanged. The classic signal is the NVI against its
255-period EMA: above means the quiet-money trend is up.

Columns:
    nvi     -- cumulative index starting at 1000, updated only when
               volume falls bar-over-bar
    nvi_ema -- EMA(255) of NVI
    atr     -- Wilder ATR(14) for the risk layer

The loop reads only bars up to and including the current bar, so
the indicators are strictly causal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

EMA_PERIOD = 255
START = 1000.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)
    nvi = np.full(n, START)
    for i in range(1, n):
        if v[i] < v[i - 1] and c[i - 1] != 0:
            nvi[i] = nvi[i - 1] * (1.0 + (c[i] - c[i - 1]) / c[i - 1])
        else:
            nvi[i] = nvi[i - 1]
    df["nvi"] = nvi
    df["nvi_ema"] = B.ema(df["nvi"], EMA_PERIOD)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
