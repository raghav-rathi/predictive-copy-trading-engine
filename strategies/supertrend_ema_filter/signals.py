"""Supertrend + EMA(200) filter signals.

Entry on the Supertrend flip, but only in the EMA(200) regime
direction:

  Long entry:  Supertrend flips to up (+1) while close > EMA(200).
  Short entry: Supertrend flips to down (-1) while close < EMA(200).
  Long exit:   Supertrend flips back to down.
  Short exit:  Supertrend flips back to up.

The EMA filter does not gate exits: once in a trade, the flip back
exits regardless of where price sits vs EMA(200).

All inputs are computed from data through bar i's close, so signals on
bar i use no future data. The harness executes at bar i+1's open.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    flip_up = (df["st_dir"] == 1) & (df["st_dir_prev"] == -1)
    flip_dn = (df["st_dir"] == -1) & (df["st_dir_prev"] == 1)
    above_ema = (df["c"] > df["ema_200"]).fillna(False)
    below_ema = (df["c"] < df["ema_200"]).fillna(False)
    df["long_entry"] = (flip_up & above_ema).fillna(False).astype(bool)
    df["short_entry"] = (flip_dn & below_ema).fillna(False).astype(bool)
    df["long_exit"] = flip_dn.fillna(False).astype(bool)
    df["short_exit"] = flip_up.fillna(False).astype(bool)
    return df
