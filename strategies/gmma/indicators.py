"""GMMA indicators (Daryl Guppy, Trend Trading).

Twelve EMAs of close split into two behavioral groups:
  trader/short group  : periods 3, 5, 8, 10, 12, 15
  investor/long group : periods 30, 35, 40, 45, 50, 60

Per bar the group extremes are computed:
  short_min = min(short-group EMAs), short_max = max(short-group EMAs)
  long_min  = min(long-group EMAs),  long_max  = max(long-group EMAs)

A bullish configuration is short_min > long_max (every trader EMA above
every investor EMA); a bearish one is short_max < long_min. Group
separation columns (short group center minus long group center, and the
two cross-gap columns) are stored for the calibration note. All values
use only bars through the current close (base.ema is a causal ewm).
"""

import pandas as pd

from strategies import base as B

SHORT_PERIODS = [3, 5, 8, 10, 12, 15]
LONG_PERIODS = [30, 35, 40, 45, 50, 60]
ATR_N = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    short_cols = []
    for n in SHORT_PERIODS:
        col = f"ema_s_{n}"
        df[col] = B.ema(df["c"], n)
        short_cols.append(col)
    long_cols = []
    for n in LONG_PERIODS:
        col = f"ema_l_{n}"
        df[col] = B.ema(df["c"], n)
        long_cols.append(col)
    df["short_min"] = df[short_cols].min(axis=1)
    df["short_max"] = df[short_cols].max(axis=1)
    df["long_min"] = df[long_cols].min(axis=1)
    df["long_max"] = df[long_cols].max(axis=1)
    # group separation: centers and the two cross-gaps
    short_center = (df["short_min"] + df["short_max"]) / 2
    long_center = (df["long_min"] + df["long_max"]) / 2
    df["gmma_sep"] = short_center - long_center
    df["gmma_bull_gap"] = df["short_min"] - df["long_max"]
    df["gmma_bear_gap"] = df["short_max"] - df["long_min"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
