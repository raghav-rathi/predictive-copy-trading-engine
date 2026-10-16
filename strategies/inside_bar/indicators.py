"""Inside-bar breakout indicators.

An inside bar has a lower high and a higher low than the bar before it
(the "mother" bar). Mother-bar extremes are carried forward as breakout
levels. Trend bias comes from a 50-period EMA and its 5-bar slope.
"""

import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame, ema_n: int = 50, slope_n: int = 5) -> pd.DataFrame:
    df = df.copy()
    df["inside"] = (
        (df["h"] < df["h"].shift(1)) & (df["l"] > df["l"].shift(1))
    ).fillna(False).astype(bool)
    df["mother_high"] = df["h"].shift(1)
    df["mother_low"] = df["l"].shift(1)
    df["ema50"] = B.ema(df["c"], ema_n)
    df["ema50_slope"] = df["ema50"] - df["ema50"].shift(slope_n)
    df["long_bias"] = ((df["c"] > df["ema50"]) & (df["ema50_slope"] > 0)).fillna(False).astype(bool)
    df["short_bias"] = ((df["c"] < df["ema50"]) & (df["ema50_slope"] < 0)).fillna(False).astype(bool)
    return df
