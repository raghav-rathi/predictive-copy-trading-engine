"""Stochastic-hook (Anti) indicators (Linda Raschke, Street Smarts).

rawK = 100 * (c - lowest(l,7)) / (highest(h,7) - lowest(l,7));
slowK = SMA(rawK, 10); trig = SMA(slowK, 4). Trend bias from EMA(50):
close above -> up-bias, below -> down-bias. Flat 7-bar windows give a
neutral rawK of 50. No lookahead: all rolling values use only bars
through the current close.
"""

import pandas as pd

from strategies import base as B

K_N = 7
SLOW_N = 10
TRIG_N = 4
EMA_TREND = 50
ATR_N = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hh = df["h"].rolling(K_N, min_periods=K_N).max()
    ll = df["l"].rolling(K_N, min_periods=K_N).min()
    denom = (hh - ll).replace(0, pd.NA)
    rawK = 100 * (df["c"] - ll) / denom
    df["rawK"] = rawK.fillna(50.0)
    df["slowK"] = B.sma(df["rawK"], SLOW_N)
    df["trig"] = B.sma(df["slowK"], TRIG_N)
    df["slowK_rising"] = (df["slowK"] > df["slowK"].shift(1)).fillna(False)
    df["rawK_rising"] = (df["rawK"] > df["rawK"].shift(1)).fillna(False)
    df["bias_up"] = (df["c"] > B.ema(df["c"], EMA_TREND)).fillna(False)
    df["bias_dn"] = (df["c"] < B.ema(df["c"], EMA_TREND)).fillna(False)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
