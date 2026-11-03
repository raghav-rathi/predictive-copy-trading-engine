"""Cardwell RSI Ranges signals.

Andrew Cardwell range rules on Wilder RSI (14): a bull range holds RSI between 40-80 (20-bar min >= 40), a bear range between 20-60 (20-bar max <= 60). Long on RSI cross above 50 inside a bull range, short on cross below 50 inside a bear range; exits at the range edges (40 / 60).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up50 = B.crossed_above(df["rsi"], 50).fillna(False)
    down50 = B.crossed_below(df["rsi"], 50).fillna(False)
    df["long_entry"] = (df["bull_range"] & up50).astype(bool)
    df["short_entry"] = (df["bear_range"] & down50).astype(bool)
    df["long_exit"] = B.crossed_below(df["rsi"], 40).fillna(False).astype(bool)
    df["short_exit"] = B.crossed_above(df["rsi"], 60).fillna(False).astype(bool)
    return df
