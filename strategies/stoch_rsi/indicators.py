"""StochRSI indicators (Tushar Chande & Stanley Kroll, 1994).

StochRSI applies the stochastic oscillator formula to Wilder's RSI:

    RSI  = Wilder RSI over RSI_LEN bars (classic: 14)
    StochRSI = (RSI - min(RSI, STOCH_LEN)) / (max(RSI, STOCH_LEN) - min(RSI, STOCH_LEN))
    %K = SMA(StochRSI, K_SMOOTH)   (classic: 3)
    %D = SMA(%K, D_SMOOTH)         (classic: 3)

All columns are 0-100. Division-by-zero (flat RSI window) yields NaN
rather than a fake extreme -- those bars simply generate no signals.
No lookahead: every bar uses only data through that bar's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

RSI_LEN = 14
STOCH_LEN = 14
K_SMOOTH = 3
D_SMOOTH = 3


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsi_v = B.rsi(df["c"], RSI_LEN)
    lo = rsi_v.rolling(STOCH_LEN, min_periods=STOCH_LEN).min()
    hi = rsi_v.rolling(STOCH_LEN, min_periods=STOCH_LEN).max()
    span = (hi - lo).replace(0, np.nan)
    stoch = (rsi_v - lo) / span * 100.0
    df["rsi"] = rsi_v
    df["stochrsi"] = stoch
    df["stochrsi_k"] = stoch.rolling(K_SMOOTH, min_periods=K_SMOOTH).mean()
    df["stochrsi_d"] = df["stochrsi_k"].rolling(D_SMOOTH, min_periods=D_SMOOTH).mean()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
