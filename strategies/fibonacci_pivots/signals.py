"""Fibonacci Pivots signals.

Fibonacci pivot points on 1h bars: levels from the prior completed 24-bar block (pivot = (H+L+C)/3; R1 = P + 0.382*(H-L), S1 = P - 0.382*(H-L)). Long on close cross above R1, short on cross below S1; exits on cross back through the pivot. Levels are fixed within a block — no intraday repainting.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["c"], df["r1"]).fillna(False)
    down = B.crossed_below(df["c"], df["s1"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = down.astype(bool)
    df["long_exit"] = B.crossed_below(df["c"], df["pivot"]).fillna(False).astype(bool)
    df["short_exit"] = B.crossed_above(df["c"], df["pivot"]).fillna(False).astype(bool)
    return df
