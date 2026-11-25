"""Detrended Price Oscillator (DPO) indicators (StockCharts
ChartSchool).

    DPO(20) = close - SMA(close, 20) shifted back 11 bars
              (displacement = 20/2 + 1 = 11)

Concretely, DPO[i] = close[i] - SMA20[i - 11]: the 20-bar
simple moving average as it stood 11 bars ago, subtracted
from the current close. This is the causal, real-time
reading of the task specification (and the MetaStock
"Technical Analysis from A to Z" formula: "subtract the
moving average (n/2)+1 days ago from the closing price").

It is NOT StockCharts' centered plotting convention, in
which the DPO value for a bar is that bar's price minus the
20-day SMA ending 11 bars in the future — that version uses
future data and cannot be traded in real time. The centered
version and this version are the same series shifted by 11
bars; only this causal one is computed here, so every value
on bar i uses data through bar i's close only (the SMA
itself uses closes through bar i - 11).

Columns:
    dpo -- Detrended Price Oscillator
    atr -- ATR(14) for the harness
"""

import pandas as pd

from strategies import base as B

PERIOD = 20


def add_indicators(df: pd.DataFrame, period: int = PERIOD) -> pd.DataFrame:
    df = df.copy()
    shift = period // 2 + 1
    sma = B.sma(df["c"], period)
    df["dpo"] = df["c"] - sma.shift(shift)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
