"""Detrended Price Oscillator (DPO) -- trend-filtered zero-line crosses.

    DPO(n)  = close - SMA(close, n).shift(n // 2 + 1)
    trend   = SMA(close, ma)          -- regime filter

DPO removes the trend from price: it subtracts the n-bar SMA displaced
back by half the lookback (plus one bar, the standard Investopedia /
Ehlers convention), so the oscillator shows where price sits relative
to its own lagged mean -- i.e. the position inside the dominant cycle.
A zero-line cross marks the cycle turning.

Columns:

    dpo    -- DPO(n)
    sma_ma -- SMA(close, ma), the trend filter
    atr    -- Wilder ATR(14) for the risk layer

No lookahead: SMA(close, n).shift(n//2 + 1) on bar j uses closes
through bar j - (n//2 + 1) only; the first fully-formed DPO arrives
after n + (n//2 + 1) - 1 bars, the trend SMA after ma - 1 bars.
"""

import pandas as pd

from strategies import base as B

DPO_N = 20  # shipped default
TREND_MA = 50  # shipped default


def dpo(c: pd.Series, n: int = DPO_N) -> pd.Series:
    """Detrended Price Oscillator from the close series."""
    lag = n // 2 + 1
    return c - B.sma(c, n).shift(lag)


def add_indicators(df: pd.DataFrame, n: int = DPO_N,
                   ma: int = TREND_MA) -> pd.DataFrame:
    df = df.copy()
    df["dpo"] = dpo(df["c"], n)
    df["sma_ma"] = B.sma(df["c"], ma)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
