"""Connors Cumulative RSI indicators (Larry Connors & Cesar Alvarez).

Wilder RSI(2) on the close, then the cumulative sum of (RSI(2) - 50)
over all bars, never reset:

  rsi2     -- Wilder RSI(2)
  cum_rsi  -- sum of (rsi2 - 50) from the first bar to bar i

All computation is causal: every value on bar i uses only data through
bar i's close. Note the cumulative sum drifts with history length: the
longer the series, the further cum_rsi can wander from zero, so the
+/-100 levels are absolute extremes on the cumulative scale, not a
bounded oscillator. See CALIBRATION.md.
"""

import pandas as pd

from strategies.base import rsi

RSI_N = 2

INDICATOR_COLS = [
    "rsi2",
    "cum_rsi",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi2"] = rsi(df["c"], RSI_N)
    # (RSI(2) - 50) summed over all bars; never reset. The shared
    # base.rsi fills its first-bar NaN with 0.0, so the sum is defined
    # from bar 0.
    df["cum_rsi"] = (df["rsi2"] - 50.0).cumsum()
    return df
