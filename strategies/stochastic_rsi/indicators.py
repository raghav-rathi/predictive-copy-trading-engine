"""StochRSI(14,14,3,3) cross indicators (Chande & Kroll).

rsi14 = RSI(14); stochrsi = (rsi14 - min rsi14 over 14) /
(max rsi14 over 14 - min rsi14 over 14) * 100; %K = SMA(3) of
stochrsi; %D = SMA(3) of %K. When the 14-bar RSI range is 0
(flat RSI), stochrsi is defined as 50.0.

Columns:
    rsi14       -- Wilder RSI(14)
    stochrsi    -- raw StochRSI 0-100
    stochrsi_k  -- %K, SMA(3) of stochrsi
    stochrsi_d  -- %D, SMA(3) of %K
    atr         -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

RSI_N = 14
STOCH_N = 14
K_N = 3
D_N = 3

INDICATOR_COLS = ["rsi14", "stochrsi", "stochrsi_k", "stochrsi_d", "atr"]


def add_indicators(df: pd.DataFrame, rsi_n: int = RSI_N,
                   stoch_n: int = STOCH_N, k_n: int = K_N,
                   d_n: int = D_N) -> pd.DataFrame:
    df = df.copy()
    df["rsi14"] = B.rsi(df["c"], rsi_n)
    rsi_min = df["rsi14"].rolling(stoch_n, min_periods=stoch_n).min()
    rsi_max = df["rsi14"].rolling(stoch_n, min_periods=stoch_n).max()
    rng = rsi_max - rsi_min
    df["stochrsi"] = np.where(
        rng == 0, 50.0, (df["rsi14"] - rsi_min) / rng.replace(0, np.nan) * 100.0)
    df["stochrsi_k"] = B.sma(df["stochrsi"], k_n)
    df["stochrsi_d"] = B.sma(df["stochrsi_k"], d_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
