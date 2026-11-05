"""VWMA(10) vs VWMA(50) crossover indicators.

VWMA(n) = sum(close * volume) / sum(volume) over n bars.
"""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["vwma_fast", "vwma_slow", "atr"]


def _vwma(c: pd.Series, v: pd.Series, n: int) -> pd.Series:
    pv = (c * v).rolling(n, min_periods=n).sum()
    vv = v.rolling(n, min_periods=n).sum()
    return pv / vv.replace(0, float("nan"))


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["vwma_fast"] = _vwma(df["c"], df["v"], 10)
    df["vwma_slow"] = _vwma(df["c"], df["v"], 50)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
