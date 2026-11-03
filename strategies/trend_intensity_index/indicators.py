"""Trend Intensity Index indicators.

M.H. Pee Trend Intensity Index (30): 100 x sum of up-moves / sum of absolute moves. Long on cross above 80 (strong uptrend), short on cross below 20 (strong downtrend); exits on cross back through 50.
"""

import pandas as pd

from strategies import base as B

PERIOD = 30


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    delta = df["c"].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    up_sum = up.rolling(PERIOD, min_periods=PERIOD).sum()
    down_sum = down.rolling(PERIOD, min_periods=PERIOD).sum()
    total = up_sum + down_sum
    df["tii"] = (100.0 * up_sum / total.replace(0, float("nan"))).fillna(50.0)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
