"""Band-walk entries on first outside close; mid-band exits."""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_e = B.crossed_above(df["c"], df["bb_upper"])
    short_e = B.crossed_below(df["c"], df["bb_lower"])
    df["long_entry"] = long_e.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = short_e.fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = B.crossed_below(df["c"], df["bb_mid"]).fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = B.crossed_above(df["c"], df["bb_mid"]).fillna(False).to_numpy(dtype=bool)
    return df
