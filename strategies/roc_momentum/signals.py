"""ROC zero-cross signals: long on cross above 0, short below, exit opposite."""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    r = df["roc"]
    up = B.crossed_above(r, 0.0)
    down = B.crossed_below(r, 0.0)
    df["long_entry"] = up.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = down.fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = down.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = up.fillna(False).to_numpy(dtype=bool)
    return df
