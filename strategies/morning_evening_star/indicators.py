"""Star pattern inputs: bodies, midpoints, gaps."""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["body"] = df["c"] - df["o"]
    df["mid"] = (df["o"] + df["c"]) / 2
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
