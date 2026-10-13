"""Alexander Elder Force Index (Trading for a Living, Wiley 1993).

Force Index = (close - prev close) * volume: combines price momentum and
volume into one number. Elder smooths it two ways:
  * FI13 = EMA(FI, 13) -- the trend: sign tells which side the force is on.
  * FI2  = EMA(FI, 2)  -- the trigger: fast hook used for entries/exits.

Pure pandas/numpy, no lookahead (all EMA inputs end at bar i).
"""

import pandas as pd

from strategies import base as B

FI_TREND_N = 13    # Elder's trend smoothing
FI_TRIGGER_N = 2   # Elder's trigger smoothing
ATR_N = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fi = (df["c"] - df["c"].shift(1)) * df["v"]
    df["fi_raw"] = fi
    df["fi13"] = B.ema(fi, FI_TREND_N)
    df["fi2"] = B.ema(fi, FI_TRIGGER_N)
    df["fi13_prev"] = df["fi13"].shift(1)
    df["fi2_prev"] = df["fi2"].shift(1)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
