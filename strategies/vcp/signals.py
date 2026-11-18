"""Volatility Contraction Pattern (VCP) signals.

Long entry: a VCP base is valid AND the Stage-2 uptrend filter
holds (close > SMA(50) AND SMA(50) > SMA(200)) AND the close breaks
above the pivot (high of the last contraction) AND volume expands
(volume > 1.5x SMA(volume, 50)). Short entry: the symmetric mirror
— short base valid, downtrend filter (close < SMA(50) AND
SMA(50) < SMA(200)), close below the pivot low, volume expansion.

Long exit: close back below the pivot (failed breakout) OR the
opposite VCP signal prints. Short exit: the mirror.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open). The pivot is the level of the
last completed contraction, known at bar i's close at the latest.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    uptrend = ((df["c"] > df["sma50"]) & (df["sma50"] > df["sma200"])).fillna(False)
    downtrend = ((df["c"] < df["sma50"]) & (df["sma50"] < df["sma200"])).fillna(False)
    vol_exp = (df["v"] > 1.5 * df["vol_ma50"]).fillna(False)
    bull_break = (df["c"] > df["pivot_high"]).fillna(False)
    bear_break = (df["c"] < df["pivot_low"]).fillna(False)
    long_sig = (df["vcp_valid"].fillna(False) & uptrend & bull_break & vol_exp)
    short_sig = (df["vcp_valid_short"].fillna(False) & downtrend & bear_break & vol_exp)
    df["long_entry"] = long_sig.astype(bool)
    df["short_entry"] = short_sig.astype(bool)
    df["long_exit"] = (((df["c"] < df["pivot_high"]).fillna(False)) | short_sig).astype(bool)
    df["short_exit"] = (((df["c"] > df["pivot_low"]).fillna(False)) | long_sig).astype(bool)
    return df
