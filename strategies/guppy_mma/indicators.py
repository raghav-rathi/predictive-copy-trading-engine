"""Guppy Multiple Moving Average indicators (Daryl Guppy).

Two EMA ribbons: the short-term group tracks traders, the long-term
group tracks investors. Each group's mean is the ribbon's center line.

Columns:
    short_mean -- mean of EMA(3/5/8/10/12/15) of close
    long_mean  -- mean of EMA(30/35/40/45/50/60) of close
    atr        -- Wilder ATR(14) for the risk layer

All windows use only bars up to and including the current bar, so
the indicators are strictly causal.
"""

import pandas as pd

from strategies import base as B

SHORT_PERIODS = (3, 5, 8, 10, 12, 15)
LONG_PERIODS = (30, 35, 40, 45, 50, 60)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    short = pd.concat([B.ema(df["c"], n) for n in SHORT_PERIODS], axis=1)
    long = pd.concat([B.ema(df["c"], n) for n in LONG_PERIODS], axis=1)
    df["short_mean"] = short.mean(axis=1)
    df["long_mean"] = long.mean(axis=1)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
