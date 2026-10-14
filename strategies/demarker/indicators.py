"""DeMarker (DeM) indicators — Tom DeMark, "The New Science of Technical Analysis".

DeMax[i] = max(h[i] - h[i-1], 0)   (demand-side move)
DeMin[i] = max(l[i-1] - l[i], 0)   (supply-side move)
DeM = SMA(DeMax, N) / (SMA(DeMax, N) + SMA(DeMin, N)), range 0..1

DeMark's reading: 0.3 and below = oversold/exhaustion risk,
0.7 and above = overbought/exhaustion risk. A flat market (both SMA
legs zero) defines DeM = 0.5 by convention to avoid a divide-by-zero.
No lookahead: DeMax/DeMin use only the current and previous bar's
high/low; the SMA uses bars through the current close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 14  # DeMark's canonical period


def demarker(h: pd.Series, l: pd.Series, n: int = PERIOD) -> pd.DataFrame:
    dh = h.diff()
    dl = -l.diff()  # l[i-1] - l[i]
    demax = dh.clip(lower=0)
    demin = dl.clip(lower=0)
    sma_max = B.sma(demax, n)
    sma_min = B.sma(demin, n)
    denom = sma_max + sma_min
    raw = sma_max / denom
    # guard: both legs zero (dead-flat market) -> 0.5; keep NaN where the
    # SMA window isn't full yet.
    val = np.where(denom > 0, raw, np.where(denom == 0, 0.5, np.nan))
    dem = pd.Series(val, index=h.index).clip(0.0, 1.0)
    return pd.DataFrame({"demax": demax, "demin": demin, "dem": dem})


def add_indicators(df: pd.DataFrame, n: int = PERIOD) -> pd.DataFrame:
    df = df.copy()
    d = demarker(df["h"], df["l"], n)
    df["demax"] = d["demax"]
    df["demin"] = d["demin"]
    df["dem"] = d["dem"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
