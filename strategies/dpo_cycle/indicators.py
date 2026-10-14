"""Detrended Price Oscillator (DPO) indicators — cycle timing.

DPO strips the long-term trend so short cycles stand out:

    DPO[i] = C[i] - SMA(C, N)[i - (N/2 + 1)]

Textbook DPO compares price to a moving average displaced (N/2+1) bars
into the past/future to center it on the cycle. The chart-school form
peeks into the future; this engine uses the strictly causal version:
today's close minus the SMA value from (N/2+1) bars ago, i.e. price vs
the trend estimate that was centered 11 bars back. No lookahead:
SMA(N)[i-11] uses only data through bar i-11.

Zero-line crosses mark the cycle turning: above zero = price above its
detrended trend (bullish cycle phase), below = bearish phase.
"""

import pandas as pd

from strategies import base as B

N = 21  # cycle window; displacement = N//2 + 1 = 11
DISP = N // 2 + 1


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sma = B.sma(df["c"], N)
    df["dpo"] = df["c"] - sma.shift(DISP)
    return df
