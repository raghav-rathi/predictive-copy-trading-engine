"""Williams %R signals: oversold/overbought exits with SMA(50) trend filter."""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    wr = df["williams_r"]
    df["long_entry"] = (B.crossed_above(wr, -80) & (df["c"] > df["sma50"])).astype(bool)
    df["short_entry"] = (B.crossed_below(wr, -20) & (df["c"] < df["sma50"])).astype(bool)
    df["long_exit"] = B.crossed_above(wr, -20).astype(bool)
    df["short_exit"] = B.crossed_below(wr, -80).astype(bool)
    return df
