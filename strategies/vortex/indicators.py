"""Vortex indicator (Etienne Botes & Douglas Siepman, S&C Jan 2010).

VM+ = |high - prior low|; VM- = |low - prior high|
VI+ = sum(VM+, n) / sum(TR, n); VI- = sum(VM-, n) / sum(TR, n)

Pure pandas/numpy; no lookahead (all rolling sums use data through bar i).
"""

import pandas as pd

from strategies import base as B

VI_PERIOD = 14
ADX_PERIOD = 14
ADX_THRESHOLD = 20.0


def add_indicators(df: pd.DataFrame, vi_n: int = VI_PERIOD) -> pd.DataFrame:
    df = df.copy()
    vm_plus = (df["h"] - df["l"].shift(1)).abs()
    vm_minus = (df["l"] - df["h"].shift(1)).abs()
    tr = B.true_range(df["h"], df["l"], df["c"])
    tr_sum = tr.rolling(vi_n, min_periods=vi_n).sum()
    df["vi_plus"] = vm_plus.rolling(vi_n, min_periods=vi_n).sum() / tr_sum
    df["vi_minus"] = vm_minus.rolling(vi_n, min_periods=vi_n).sum() / tr_sum
    df["vi_plus_prev"] = df["vi_plus"].shift(1)
    df["vi_minus_prev"] = df["vi_minus"].shift(1)
    adx_df = B.adx(df["h"], df["l"], df["c"], ADX_PERIOD)
    df["adx"] = adx_df["adx"]
    return df
