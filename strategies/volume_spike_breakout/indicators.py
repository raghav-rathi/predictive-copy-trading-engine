"""Volume-spike breakout: rolling 20-bar extremes + volume vs its average.

Prior-bar extremes are used (shifted), so a bar cannot break its own high.
"""

import numpy as np
import pandas as pd

from strategies import base as B

N = 20
VOL_MULT = 2.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["vs_high"] = df["h"].shift(1).rolling(N, min_periods=N).max()
    df["vs_low"] = df["l"].shift(1).rolling(N, min_periods=N).min()
    df["vol_avg"] = df["v"].shift(1).rolling(N, min_periods=N).mean()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
