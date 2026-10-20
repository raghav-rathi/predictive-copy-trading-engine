"""Cup and Handle indicators (William O'Neil), adapted to 1h crypto.

The pattern needs a prior uptrend plus volatility/volume context:

  sma50        -- 50-bar simple moving average of close
  uptrend      -- True when close > sma50 on each of the last 30 bars
  vol_avg20    -- 20-bar average volume
  vol_ratio    -- v / vol_avg20 (breakout confirmation uses 1.4x)
  atr          -- ATR(14) for risk scaling and the cup-depth ATR band

Pattern geometry itself (rims, bottom, handle) is detected in signals.py
because it needs argmax/argmin placement, not just rolling scalars.

All columns use data through bar i only -- no lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B

SMA_N = 50
TREND_BARS = 30
VOL_N = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    df["sma50"] = B.sma(c, SMA_N)
    above = (c > df["sma50"]).fillna(False)
    df["uptrend"] = (
        above.rolling(TREND_BARS, min_periods=TREND_BARS).sum() == TREND_BARS
    )
    df["vol_avg20"] = df["v"].rolling(VOL_N, min_periods=VOL_N).mean()
    df["vol_ratio"] = df["v"] / df["vol_avg20"].replace(0, np.nan)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
