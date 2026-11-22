"""Oliver Kell 20-EMA Reclaim indicators (causal, no lookahead).

Pipeline, computed bar by bar using only data through bar i
(daily periods from the source map directly to 1h periods):

1. Trend filter: price above a RISING 200 SMA, with the 10 and
   20 EMAs also rising — the source's "leader" filter (a stock
   making new highs after a "wedge pop"; the wedge pop itself is
   a chart pattern with no formal rule, so the rising-200/EMA
   filter is the operational proxy — see CALIBRATION.md).
2. Pullback: the lowest low of the trailing 20 bars sits 5-19%
   below the trailing-20-bar highest high, and the close dipped
   below the 20 EMA at least once in the prior 10 bars (the
   pullback "to/below" the 20 EMA).
3. Quiet volume: the current bar's volume is below its 20-bar
   average — the source's pullback on quiet volume.

Columns:

    sma200 / sma200_rising -- 200 SMA and whether it rose vs bar i-1
    ema10 / ema20 / ema10_rising / ema20_rising
    recent_high_20 -- trailing-20-bar highest high
    pullback_low_20 -- trailing-20-bar lowest low
    pullback_depth -- (recent_high - pullback_low) / recent_high
    touched_ema20 -- close was below the 20 EMA in bars i-10..i-1
    vol_avg20 / quiet_vol -- 20-bar average volume, v < average
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every rolling window is trailing (includes bar i,
excludes later bars); ``touched_ema20`` reads only bars before i.
"""

import numpy as np
import pandas as pd

from strategies import base as B

SMA_N = 200
EMA_FAST = 10
EMA_MID = 20
LOOKBACK = 20
TOUCHBACK = 10
DEPTH_LO, DEPTH_HI = 0.05, 0.19


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l, v = df["c"], df["h"], df["l"], df["v"]
    df["sma200"] = B.sma(c, SMA_N)
    df["sma200_rising"] = (df["sma200"] > df["sma200"].shift(1)).fillna(False)
    df["sma200_falling"] = (df["sma200"] < df["sma200"].shift(1)).fillna(False)
    df["ema10"] = B.ema(c, EMA_FAST)
    df["ema20"] = B.ema(c, EMA_MID)
    df["ema10_rising"] = (df["ema10"] > df["ema10"].shift(1)).fillna(False)
    df["ema20_rising"] = (df["ema20"] > df["ema20"].shift(1)).fillna(False)
    df["ema10_falling"] = (df["ema10"] < df["ema10"].shift(1)).fillna(False)
    df["ema20_falling"] = (df["ema20"] < df["ema20"].shift(1)).fillna(False)
    df["recent_high_20"] = h.rolling(LOOKBACK, min_periods=LOOKBACK).max()
    df["pullback_low_20"] = l.rolling(LOOKBACK, min_periods=LOOKBACK).min()
    df["pullback_depth"] = (
        (df["recent_high_20"] - df["pullback_low_20"])
        / df["recent_high_20"]
    )
    below = (c < df["ema20"]).astype(float)
    above = (c > df["ema20"]).astype(float)
    # Did the close dip below the 20 EMA in the 10 bars before i?
    df["touched_ema20"] = (
        below.shift(1).rolling(TOUCHBACK, min_periods=1).max() > 0
    ).fillna(False)
    # Mirror for shorts: did the close poke above the 20 EMA before i?
    df["touched_ema20_above"] = (
        above.shift(1).rolling(TOUCHBACK, min_periods=1).max() > 0
    ).fillna(False)
    df["vol_avg20"] = v.rolling(LOOKBACK, min_periods=LOOKBACK).mean()
    df["quiet_vol"] = (v < df["vol_avg20"]).fillna(False)
    df["atr"] = B.atr(h, l, c, 14)
    return df
