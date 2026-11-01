"""Inverse Fisher RSI indicators (John Ehlers).

Ehlers' recipe, exactly as published: a 5-bar RSI is translated to
(-50, +50) by subtracting 50, scaled by 0.1 into (-5, +5), smoothed
with a 9-bar linearly weighted average, and compressed by the Inverse
Fisher Transform (e^(2v)-1)/(e^(2v)+1) = tanh(v). The output is
bipolar: it sits near +1 in uptrends and near -1 in downtrends, so
threshold crossings are sharp and unambiguous.

Columns:
    ifish -- Inverse Fisher Transform of the smoothed 5-bar RSI
    atr   -- Wilder ATR(14) for the risk layer

All windows use only bars up to and including the current bar, so
the indicators are strictly causal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

RSI_PERIOD = 5
WMA_PERIOD = 9


def _wma(s: pd.Series, n: int) -> pd.Series:
    weights = np.arange(1, n + 1, dtype=float)
    denom = weights.sum()

    def _w(window):
        return float(np.dot(window, weights) / denom)

    return s.rolling(n, min_periods=n).apply(_w, raw=True)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    r = B.rsi(df["c"], RSI_PERIOD)
    v1 = 0.1 * (r - 50.0)
    v2 = _wma(v1, WMA_PERIOD)
    df["ifish"] = np.tanh(v2)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
