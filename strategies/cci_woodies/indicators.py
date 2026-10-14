"""Woodies CCI indicators (Ken Wood's Commodity Channel Index system).

CCI(n) = (TP - SMA(TP, n)) / (0.015 * mean(|TP - SMA(TP, n)|)), TP=(h+l+c)/3.
Default n=14. The 0.015 Lambert constant puts ~70-80% of readings inside
+-100, so excursions beyond are the "extreme" Woodies watches. This module
also exposes the 20-bar hook state: whether CCI has printed below -100
(within the last 20 bars) for the long setup, or above +100 for the short.
All causal: only data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

N = 14           # CCI period (Lambert's classic)
HOOK = 100.0     # extreme threshold
HOOK_BARS = 20   # lookback for the hook print


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    sma_tp = B.sma(tp, N)
    md = (tp - sma_tp).abs().rolling(N, min_periods=N).mean()
    cci = (tp - sma_tp) / (0.015 * md.replace(0, np.nan))
    df["cci"] = cci
    df["cci_min20"] = cci.rolling(HOOK_BARS, min_periods=1).min()
    df["cci_max20"] = cci.rolling(HOOK_BARS, min_periods=1).max()
    return df
