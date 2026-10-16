"""Time-series momentum indicators (Liu & Tsyvinski 2021; Liu, Tsyvinski & Wu 2022).

Volatility-scaled past returns at 1-week (168 bars) and 4-week (672 bars)
horizons on 1h candles:

    r168 = (c / c.shift(168) - 1) / std(ret1, 168)
    r672 = (c / c.shift(672) - 1) / std(ret1, 672)

The ratios are the same z-scored returns as the paper's 1-week / 4-week
signals.  No-lookahead convention: the ratio at bar i uses only data
through bar i, but because the ratio *includes* the current bar's return
in its vol window, the harness convention (cf. donchian's prior-bar
channels) shifts them by one bar before signal evaluation:
r168_s = r168.shift(1), r672_s = r672.shift(1). Signals on bar i fire
off data through bar i-1 and execute at bar i+1's open.
"""

import numpy as np
import pandas as pd

from strategies import base as B

SHORT_N = 168  # 1 week on 1h bars
LONG_N = 672   # 4 weeks on 1h bars
ATR_N = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    ret1 = c.pct_change()
    vol168 = ret1.rolling(SHORT_N, min_periods=SHORT_N).std().replace(0, np.nan)
    vol672 = ret1.rolling(LONG_N, min_periods=LONG_N).std().replace(0, np.nan)
    r168 = (c / c.shift(SHORT_N) - 1) / vol168
    r672 = (c / c.shift(LONG_N) - 1) / vol672
    df["r168"] = r168
    df["r672"] = r672
    # strict no-lookahead shift: ratio formed with the current bar is only
    # usable for the *next* bar's signal
    df["r168_s"] = df["r168"].shift(1)
    df["r672_s"] = df["r672"].shift(1)
    df["atr"] = B.atr(df["h"], df["l"], c, ATR_N)
    return df
