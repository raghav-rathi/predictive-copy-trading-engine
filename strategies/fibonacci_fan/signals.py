"""Fibonacci Fan signals.

Fibonacci fan (rolling 50-bar leg): fan lines radiate from the window low through the 38.2% and 61.8% retracement points of the low-to-high leg, extended forward at the leg's slope. Long on close cross above the 38.2% fan line, short on cross below the 61.8% fan line; exits on the opposite cross. Redrawn each bar from data through that bar only — no repainting of past signals.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["c"], df["fan382"]).fillna(False)
    down = B.crossed_below(df["c"], df["fan618"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = down.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
