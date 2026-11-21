"""Stochastic RSI Crossover indicators.

StochRSI(14, 14, 3, 3) (Tushar Chande & Stanley Kroll, 1994):

    RSI14 = RSI(14) of close (Wilder, via strategies.base.rsi)
    %K    = 100 * (RSI14 - min RSI14 over last 14 bars)
                  / (max RSI14 over last 14 bars
                     - min RSI14 over last 14 bars)
            with a zero-range window (max == min) scored as 50
            (and the result clipped to [0, 100] against float error)
    %D    = SMA(3) of %K

Note on the (14, 14, 3, 3) naming: some platforms smooth the raw
stochastic into %K with a 3-bar SMA and then smooth again into %D.
The batch spec defines %K as the raw stochastic value above and
%D as its 3-bar SMA; that is what ships here (see CALIBRATION.md).

Columns:
    rsi14 -- RSI(14) of close
    stoch_k -- %K, 0..100 (50 on a zero-range window)
    stoch_d -- %D, SMA(3) of %K
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only; the RSI min/max windows are trailing (include bar i).
"""

import numpy as np
import pandas as pd

from strategies import base as B

RSI_N = 14
STOCH_N = 14
D_N = 3
ATR_N = 14


def add_indicators(df: pd.DataFrame, rsi_n: int = RSI_N,
                   stoch_n: int = STOCH_N, d_n: int = D_N,
                   atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    rsi = B.rsi(c, rsi_n)
    df["rsi14"] = rsi
    lo = rsi.rolling(stoch_n, min_periods=stoch_n).min()
    hi = rsi.rolling(stoch_n, min_periods=stoch_n).max()
    rng = hi - lo
    k = pd.Series(
        np.where(rng > 0, 100.0 * (rsi - lo) / rng,
                 np.where(rng == 0, 50.0, np.nan)),
        index=df.index,
    )
    df["stoch_k"] = k.clip(0.0, 100.0)
    df["stoch_d"] = B.sma(k, d_n)
    df["atr"] = B.atr(df["h"], df["l"], c, atr_n)
    return df
