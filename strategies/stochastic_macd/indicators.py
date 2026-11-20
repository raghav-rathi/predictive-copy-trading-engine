"""Stochastic %K/%D + MACD histogram indicators.

Stochastic(14,3,3) (George Lane): raw %K = 100 * (close - lowest
low of 14) / (highest high of 14 - lowest low of 14); %K =
SMA(3) of raw %K; %D = SMA(3) of %K. MACD(12,26,9) (Gerald Appel)
from strategies.base: macd line, signal line, histogram = line -
signal.

Columns:
    stoch_k / stoch_d -- %K and %D (0-100 scale)
    macd / macd_signal / macd_hist -- MACD lines
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

STOCH_N = 14
STOCH_SMOOTH = 3
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"]
    l = df["l"]
    c = df["c"]
    hh = h.rolling(STOCH_N, min_periods=STOCH_N).max()
    ll = l.rolling(STOCH_N, min_periods=STOCH_N).min()
    rng = (hh - ll).replace(0, np.nan)
    raw_k = 100.0 * (c - ll) / rng
    df["stoch_k"] = B.sma(raw_k, STOCH_SMOOTH)
    df["stoch_d"] = B.sma(df["stoch_k"], STOCH_SMOOTH)
    m = B.macd(c, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["atr"] = B.atr(h, l, c, 14)
    return df
