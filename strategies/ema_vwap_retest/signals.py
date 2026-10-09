"""EMA/VWAP breakout-retest signals.

Long setup (all must hold):
  * trend stack: close > 8 EMA > 20 EMA and close > session VWAP
  * breakout memory: close crossed above PDH within the last 12 bars
  * trigger: price back near the 8 EMA (pullback) or near PDH (retest),
    within 0.25 x ATR
Short mirrors with PDL.

Exit long when close < 8 EMA (Elly's trailing rule); exit short when
close > 8 EMA.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

RETEST_BARS = 12
TOUCH_ATR = 0.25


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    valid = df["pdh"].notna() & df["ema20"].notna() & df["vwap"].notna()
    broke_pdh = crossed_above(df["c"], df["pdh"])
    broke_pdl = crossed_below(df["c"], df["pdl"])
    # breakout memory: a break happened in the last RETEST_BARS bars
    mem_long = broke_pdh.rolling(RETEST_BARS, min_periods=1).max() > 0
    mem_short = broke_pdl.rolling(RETEST_BARS, min_periods=1).max() > 0
    stack_long = (df["c"] > df["ema8"]) & (df["ema8"] > df["ema20"]) & (df["c"] > df["vwap"])
    stack_short = (df["c"] < df["ema8"]) & (df["ema8"] < df["ema20"]) & (df["c"] < df["vwap"])
    near_ema = (df["c"] - df["ema8"]).abs() < TOUCH_ATR * df["atr"]
    near_pdh = (df["c"] - df["pdh"]).abs() < TOUCH_ATR * df["atr"]
    near_pdl = (df["c"] - df["pdl"]).abs() < TOUCH_ATR * df["atr"]
    df["long_entry"] = stack_long & mem_long & (near_ema | near_pdh) & valid
    df["short_entry"] = stack_short & mem_short & (near_ema | near_pdl) & valid
    df["long_exit"] = df["c"] < df["ema8"]
    df["short_exit"] = df["c"] > df["ema8"]
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
