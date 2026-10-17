"""Volume-weighted moving average cross indicators.

VWMA(n) = sum(price * volume, n) / sum(volume, n), price = typical (h+l+c)/3.
Fast VWMA(20) vs slow VWMA(50): the cross carries volume conviction --
moves on heavy volume shift the fast line first. Volume filter: current
volume above its 20-bar SMA. All causal.
"""

import pandas as pd

from strategies import base as B

FAST = 20
SLOW = 50
VOL_N = 20


def _vwma(tp: pd.Series, v: pd.Series, n: int) -> pd.Series:
    pv = (tp * v).rolling(n, min_periods=n).sum()
    vv = v.rolling(n, min_periods=n).sum().replace(0, float("nan"))
    return pv / vv


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tp = (df["h"] + df["l"] + df["c"]) / 3
    v = df["v"]
    df["vwma_fast"] = _vwma(tp, v, FAST)
    df["vwma_slow"] = _vwma(tp, v, SLOW)
    df["vol_ok"] = (v > B.sma(v, VOL_N)).fillna(False)
    return df
