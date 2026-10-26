"""Three soldiers / three crows: body strength and inside-open structure."""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    body = df["c"] - df["o"]
    df["body"] = body
    df["body_pct"] = body / df["c"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
