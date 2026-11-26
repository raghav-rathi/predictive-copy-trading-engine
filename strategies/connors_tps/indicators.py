"""Connors TPS indicators.

Larry Connors & Cesar Alvarez, "Short Term Trading Strategies
That Work" (2008) and "High Probability ETF Trading" — TPS =
Trend, Pullback, Setup. 1h-scaled adaptation, documented in
README.md: the book's daily 200-bar trend filter is scaled to
200 1h bars (~8.3 days), stated as an adaptation, not the
book's daily rule.

Columns:
    sma200 -- SMA(close, 200), the trend filter
    rsi2   -- Wilder RSI(2) via base.rsi
    atr14  -- ATR(14), diagnostic

Note base.rsi 0-fills on flat stretches (RSI sits at 0 where
only losses are seen, 100 where only gains): after a pure
flat stretch RSI(2) reads 0, which is below the 25 entry
level — the two-consecutive-bar rule plus the SMA(200) trend
filter are the guards, and WARMUP = 210 keeps the spin-up
out of the traded window. No lookahead: SMA and Wilder RSI
are causal.
"""

import pandas as pd

from strategies import base as B

SMA_N = 200
RSI_N = 2


def add_indicators(
    df: pd.DataFrame,
    sma_n: int = SMA_N,
    rsi_n: int = RSI_N,
) -> pd.DataFrame:
    df = df.copy()
    df[f"sma{sma_n}"] = B.sma(df["c"], sma_n)
    df["rsi2"] = B.rsi(df["c"], rsi_n)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
