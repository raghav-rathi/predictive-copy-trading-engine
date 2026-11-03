"""Cutler RSI indicators.

Cutler's RSI (14): Wilder's RSI with simple moving averages of gains/losses instead of Wilder smoothing. Long on cross above 30 from oversold, short on cross below 70 from overbought; exits at the opposite extreme.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    delta = df["c"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    ag = gain.rolling(PERIOD, min_periods=PERIOD).mean()
    al = loss.rolling(PERIOD, min_periods=PERIOD).mean()
    rs = ag / al.replace(0, float("nan"))
    rsi = 100.0 - 100.0 / (1.0 + rs)
    # al == 0 and ag > 0 -> 100; both zero -> 50 (flat market)
    rsi = rsi.where(~((al == 0) & (ag > 0)), 100.0)
    rsi = rsi.where(~((al == 0) & (ag == 0)), 50.0)
    df["rsi"] = rsi
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
