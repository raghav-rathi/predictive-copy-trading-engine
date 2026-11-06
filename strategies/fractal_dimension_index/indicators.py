"""Fractal Dimension Index (Ehlers) indicators: FDI(30) + SMA(20)."""

import numpy as np
import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["fdi30", "sma20"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = 30
    abs_chg = df["c"].diff().abs()
    sum_abs = abs_chg.rolling(n, min_periods=n).sum()
    hh = df["h"].rolling(n, min_periods=n).max()
    ll = df["l"].rolling(n, min_periods=n).min()
    span = hh - ll
    with np.errstate(divide="ignore", invalid="ignore"):
        fdi = (np.log(sum_abs) - np.log(span)) / np.log(2.0)
    fdi = pd.Series(fdi, index=df.index)
    fdi = fdi.where((sum_abs > 0) & (span > 0))
    df["fdi30"] = fdi.clip(lower=1.0, upper=2.0)
    df["sma20"] = B.sma(df["c"], 20)
    return df
