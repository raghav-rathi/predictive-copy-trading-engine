"""Kairi Relative Index indicators.

Kairi Relative Index (25): (close - SMA25) / SMA25 x 100. Mean reversion: long on recovery cross above -5 after an oversold dip, short on breakdown cross below +5 after an overbought peak; exits at the mean (0).
"""

import pandas as pd

from strategies import base as B

PERIOD = 25


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sma = B.sma(df["c"], PERIOD)
    df["kairi"] = (df["c"] - sma) / sma * 100.0
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
