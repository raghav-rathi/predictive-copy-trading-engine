"""RSI(2) mean-reversion signals (Larry Connors, 2008).

Long: close > SMA(200) AND RSI(2) <= 5 (overstretched to the downside
inside an uptrend). Short: close < SMA(200) AND RSI(2) >= 95.
Exit long when the close rises back above SMA(5); exit short when the
close falls back below SMA(5). All conditions use only data through
bar i's close — no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    sma200 = df["sma200"]
    sma5 = df["sma5"]
    rsi2 = df["rsi2"]
    df["long_entry"] = ((c > sma200) & (rsi2 <= 5)).fillna(False).astype(bool)
    df["short_entry"] = ((c < sma200) & (rsi2 >= 95)).fillna(False).astype(bool)
    df["long_exit"] = (c > sma5).fillna(False).astype(bool)
    df["short_exit"] = (c < sma5).fillna(False).astype(bool)
    return df
