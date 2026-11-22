"""StatOasis Rule 5: Double-Overbought Short Fade indicators (causal, no lookahead).

Pipeline, computed bar by bar using only data through bar i:

1. RSI(14) (Wilder, from strategies.base).
2. Williams %R(14): (highest high(14) - close) / (highest high(14)
   - lowest low(14)) * -100. %R > -10 means the close sits within
   10% of the 14-bar range top (deep overbought); %R < -90 means
   it sits within 10% of the range bottom (deep oversold).
3. SMA(100) trend: falling when SMA100[i] < SMA100[i-1], rising
   when SMA100[i] > SMA100[i-1].
4. ATR(14) for the risk layer.

Short setup (Rule 5 as published):
    RSI(14) > 70 AND Williams %R(14) > -10 AND SMA(100) falling
Long setup is the mirror (builder-added):
    RSI(14) < 30 AND Williams %R(14) < -90 AND SMA(100) rising

Columns:
    rsi14, willr14, sma100, sma100_falling, sma100_rising,
    short_setup, long_setup, atr

No lookahead: every rolling quantity reads bars <= i, and the
SMA(100) trend compares bar i with bar i-1 only.
"""

import pandas as pd

from strategies import base as B

RSI_HI = 70.0
RSI_LO = 30.0
WILLR_HI = -10.0   # within 10% of the 14-bar high
WILLR_LO = -90.0   # within 10% of the 14-bar low
WILLR_N = 14
SMA_N = 100


def williams_r(h, l, c, n: int = WILLR_N):
    hh = h.rolling(n, min_periods=n).max()
    ll = l.rolling(n, min_periods=n).min()
    rng = hh - ll
    out = (hh - c) / rng.replace(0, float("nan")) * -100.0
    return out.fillna(-50.0)  # flat range: neutral, neither setup


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]

    df["rsi14"] = B.rsi(c, 14)
    df["willr14"] = williams_r(h, l, c, WILLR_N)
    sma100 = B.sma(c, SMA_N)
    df["sma100"] = sma100
    df["sma100_falling"] = (sma100 < sma100.shift(1)).fillna(False).astype(bool)
    df["sma100_rising"] = (sma100 > sma100.shift(1)).fillna(False).astype(bool)
    df["atr"] = B.atr(h, l, c, 14)

    df["short_setup"] = (
        (df["rsi14"] > RSI_HI)
        & (df["willr14"] > WILLR_HI)
        & df["sma100_falling"]
    ).fillna(False).astype(bool)
    df["long_setup"] = (
        (df["rsi14"] < RSI_LO)
        & (df["willr14"] < WILLR_LO)
        & df["sma100_rising"]
    ).fillna(False).astype(bool)
    return df
