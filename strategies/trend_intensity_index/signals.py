"""Trend Intensity Index signals.

M.H. Pee Trend Intensity Index (30): 100 x sum of up-moves / sum of absolute moves. Long on cross above 80 (strong uptrend), short on cross below 20 (strong downtrend); exits on cross back through 50.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["tii"], 80).fillna(False)
    down = B.crossed_below(df["tii"], 20).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = B.crossed_below(df["tii"], 50).fillna(False).astype(bool)
    df["short_exit"] = B.crossed_above(df["tii"], 50).fillna(False).astype(bool)
    return df
