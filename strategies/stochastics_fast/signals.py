"""Fast stochastic %K/%D crossover signals.

Trend filter: close above SMA(200) for longs, below for shorts.
Long: %K crosses above %D while %K < 20 (oversold cross). Short:
%K crosses below %D while %K > 80. Exit a long when %K crosses
below %D or %K > 80; exit a short when %K crosses above %D or
%K < 20.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    k = df["stoch_k"]
    d = df["stoch_d"]
    c = df["c"]
    cross_up = ((k > d) & (k.shift(1) <= d.shift(1))).fillna(False)
    cross_down = ((k < d) & (k.shift(1) >= d.shift(1))).fillna(False)
    df["long_entry"] = (cross_up & (k < 20) & (c > df["sma200"])).fillna(False).astype(bool)
    df["short_entry"] = (cross_down & (k > 80) & (c < df["sma200"])).fillna(False).astype(bool)
    df["long_exit"] = (cross_down | (k > 80)).fillna(False).astype(bool)
    df["short_exit"] = (cross_up | (k < 20)).fillna(False).astype(bool)
    return df
