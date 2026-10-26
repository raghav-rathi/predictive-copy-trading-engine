"""Williams volatility breakout levels on 1h bars.

Levels are projected from the PREVIOUS bar only (no lookahead):
upper = prev close + 0.5 * prev range, lower = prev close - 0.5 * prev range.
"""

import numpy as np
import pandas as pd

from strategies import base as B

K = 0.5


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_c = df["c"].shift(1)
    prev_range = (df["h"] - df["l"]).shift(1)
    df["vb_upper"] = prev_c + K * prev_range
    df["vb_lower"] = prev_c - K * prev_range
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
