"""KAMA signals: close crossing the adaptive average with slope confirmation."""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    kama = df["kama"]
    rising = kama > kama.shift(1)
    falling = kama < kama.shift(1)
    df["long_entry"] = (B.crossed_above(df["c"], kama) & rising).astype(bool)
    df["short_entry"] = (B.crossed_below(df["c"], kama) & falling).astype(bool)
    df["long_exit"] = B.crossed_below(df["c"], kama).astype(bool)
    df["short_exit"] = B.crossed_above(df["c"], kama).astype(bool)
    return df
