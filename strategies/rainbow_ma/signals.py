"""Rainbow MA signals: break out of the whole ribbon, exit back inside."""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rising = (df["rb_fast"] > df["rb_fast"].shift(1)).fillna(False)
    falling = (df["rb_fast"] < df["rb_fast"].shift(1)).fillna(False)
    df["long_entry"] = (B.crossed_above(df["c"], df["rb_max"]).fillna(False) & rising).astype(bool)
    df["short_entry"] = (B.crossed_below(df["c"], df["rb_min"]).fillna(False) & falling).astype(bool)
    df["long_exit"] = (df["c"] < df["rb_fast"]).astype(bool)
    df["short_exit"] = (df["c"] > df["rb_fast"]).astype(bool)
    return df
