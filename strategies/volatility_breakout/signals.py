"""Breakout signals: close crosses its own projected level."""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["c"], df["vb_upper"])
    down = B.crossed_below(df["c"], df["vb_lower"])
    df["long_entry"] = up.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = down.fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = down.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = up.fillna(False).to_numpy(dtype=bool)
    return df
