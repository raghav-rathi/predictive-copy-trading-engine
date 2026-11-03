"""Cardwell RSI Ranges indicators.

Andrew Cardwell range rules on Wilder RSI (14): a bull range holds RSI between 40-80 (20-bar min >= 40), a bear range between 20-60 (20-bar max <= 60). Long on RSI cross above 50 inside a bull range, short on cross below 50 inside a bear range; exits at the range edges (40 / 60).
"""

import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = B.rsi(df["c"], 14)
    df["bull_range"] = (df["rsi"].rolling(20, min_periods=20).min() >= 40).fillna(False)
    df["bear_range"] = (df["rsi"].rolling(20, min_periods=20).max() <= 60).fillna(False)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
