"""Supertrend + EMA(200) regime-filter indicators.

Supertrend(10, 3.0) exactly as in strategies/supertrend (shared
strategies.base.supertrend primitive), plus a long-horizon regime
filter:

  st_line   -- Supertrend line (ATR-based trailing band)
  st_dir    -- Supertrend direction (+1 up / -1 down)
  ema_200   -- EMA(200) regime line: longs only above it, shorts only
               below it
  atr       -- Wilder ATR(14) for the risk layer
"""

import pandas as pd

from strategies import base as B

ST_N = 10
ST_K = 3.0
EMA_N = 200

INDICATOR_COLS = [
    "st_line",
    "st_dir",
    "st_dir_prev",
    "ema_200",
    "atr",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    st = B.supertrend(df["h"], df["l"], df["c"], ST_N, ST_K)
    df["st_line"] = st["supertrend"]
    df["st_dir"] = st["supertrend_dir"]
    df["st_dir_prev"] = df["st_dir"].shift(1)
    df["ema_200"] = B.ema(df["c"], EMA_N)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
