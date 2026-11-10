"""Pocket pivot indicators (Gil Morales & Chris Kacher).

Day-scale rules from "Trade Like an O'Neil Disciple" (2010), expressed in
1h bars: 1 trading day = 24 bars, 10 days = 240 bars, 50 days = 1200 bars.

All computation is causal: every value on bar i uses only data through
bar i's close.

  ema_240   -- EMA(240): 10-day moving-average analogue.
  ema_1200  -- EMA(1200): 50-day moving-average analogue.
  ema_240_rising -- EMA(240) above its own value 24 bars ago (1 day).
  max_down_vol_240 -- largest volume of any DOWN bar (close < open)
    over the previous 240 bars, excluding the current bar.
"""

import numpy as np
import pandas as pd

from strategies.base import ema

EMA_FAST = 240   # 10 trading days
EMA_SLOW = 1200  # 50 trading days
VOL_WINDOW = 240  # previous 10 trading days
RISE_LAG = 24    # 1 trading day

INDICATOR_COLS = [
    "ema_240",
    "ema_1200",
    "ema_240_rising",
    "max_down_vol_240",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    df["ema_240"] = ema(c, EMA_FAST)
    df["ema_1200"] = ema(c, EMA_SLOW)
    # EMA(240) rising: above its value 24 bars (1 trading day) ago.
    df["ema_240_rising"] = df["ema_240"] > df["ema_240"].shift(RISE_LAG)
    # Volume of down bars only; max over the previous 240 bars, excluding
    # the current bar (shift(1) after the rolling max). min_periods=1 so
    # the column is defined as soon as any down bar exists in history;
    # the strategy warmup (1250 bars) keeps trading gated until the full
    # 240-bar window and both EMAs are available anyway.
    down_vol = df["v"].where(df["c"] < df["o"], np.nan)
    df["max_down_vol_240"] = (
        down_vol.rolling(VOL_WINDOW, min_periods=1).max().shift(1)
    )
    return df
