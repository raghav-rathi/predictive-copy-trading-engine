"""Stochastic + MACD dual-confirmation indicators (George C. Lane
stochastic, StockCharts ChartSchool; MACD 12/26/9 from base.macd).

    %K = 100 * (close - lowest low(14)) / (highest high(14) - lowest low(14))
    %D = SMA(%K, 3)
    MACD histogram = MACD(12,26,9) line - signal

When the 14-bar high-low range is zero (flat bars) %K is set to
50.0 (neutral) instead of dividing by zero. Warmup NaNs are
left as NaN — they are never traded (harness warmup).

Columns:
    stoch_k    -- Fast Stochastic %K(14), 0..100
    stoch_d    -- %D = SMA(%K, 3)
    macd       -- MACD line
    macd_signal-- MACD signal line
    macd_hist  -- MACD histogram

No lookahead: every value on bar j uses data through bar j
only (rolling extremes and causal EMAs/SMAs).
"""

import numpy as np
import pandas as pd

from strategies import base as B

K_PERIOD = 14  # shipped default (StockCharts standard)
D_PERIOD = 3   # shipped default (StockCharts standard)


def add_indicators(
    df: pd.DataFrame,
    k_period: int = K_PERIOD,
    d_period: int = D_PERIOD,
) -> pd.DataFrame:
    df = df.copy()
    low_n = df["l"].rolling(k_period, min_periods=k_period).min()
    high_n = df["h"].rolling(k_period, min_periods=k_period).max()
    rng = high_n - low_n
    k = 100.0 * (df["c"] - low_n) / rng
    df["stoch_k"] = k.where(rng > 0, 50.0)
    df["stoch_d"] = B.sma(df["stoch_k"], d_period)
    m = B.macd(df["c"])
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    return df
