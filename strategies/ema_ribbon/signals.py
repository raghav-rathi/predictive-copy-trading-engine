"""EMA ribbon signals.

Full bullish alignment: ema8 > ema13 > ema21 > ema34 > ema55. Long on
the bar the alignment FIRST becomes fully bullish (not aligned on the
previous bar) AND close > ema8 AND ribbon spread (ema8 - ema55)/ema55
> 0.002 (expansion). Short: mirror — alignment first becomes fully
bearish, close < ema8, spread < -0.002. Exit a long when alignment
breaks (ema8 < ema21) or close < ema34; exit a short on the mirror
(ema8 > ema21 or close > ema34). All inputs use data through bar i's
close, so signals on bar i use no future data.
"""

import numpy as np
import pandas as pd

SPREAD_MIN = 0.002


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    e8 = df["ema8"]
    e13 = df["ema13"]
    e21 = df["ema21"]
    e34 = df["ema34"]
    e55 = df["ema55"]
    spread = df["ribbon_spread"]
    bull = (e8 > e13) & (e13 > e21) & (e21 > e34) & (e34 > e55)
    bear = (e8 < e13) & (e13 < e21) & (e21 < e34) & (e34 < e55)
    bull_first = bull & (~bull.shift(1).fillna(False))
    bear_first = bear & (~bear.shift(1).fillna(False))
    df["long_entry"] = (
        bull_first & (c > e8) & (spread > SPREAD_MIN)
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        bear_first & (c < e8) & (spread < -SPREAD_MIN)
    ).fillna(False).astype(bool)
    df["long_exit"] = ((e8 < e21) | (c < e34)).fillna(False).astype(bool)
    df["short_exit"] = ((e8 > e21) | (c > e34)).fillna(False).astype(bool)
    return df
