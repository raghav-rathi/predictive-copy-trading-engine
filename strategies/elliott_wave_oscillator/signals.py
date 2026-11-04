"""Elliott Wave Oscillator signals."""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rising = (df["sma50"] > df["sma50"].shift(1)).fillna(False)
    falling = (df["sma50"] < df["sma50"].shift(1)).fillna(False)
    df["long_entry"] = (B.crossed_above(df["ewo"], 0).fillna(False) & rising).astype(bool)
    df["short_entry"] = (B.crossed_below(df["ewo"], 0).fillna(False) & falling).astype(bool)
    df["long_exit"] = B.crossed_below(df["ewo"], 0).fillna(False).astype(bool)
    df["short_exit"] = B.crossed_above(df["ewo"], 0).fillna(False).astype(bool)
    return df
