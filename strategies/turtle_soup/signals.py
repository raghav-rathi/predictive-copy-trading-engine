"""Turtle Soup signals.

Long entry: within 3 bars after a new-20-bar-low signal bar, close back
above the violated prior 20-bar low (fade the false breakdown).
Short entry: mirror on new-20-bar-high signal bars.
Signal exits: none -- trade management is stop / chandelier trail /
target / max-hold from risk.py.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sigL = df["sig_low_bar"].fillna(False)
    sigS = df["sig_high_bar"].fillna(False)
    # violated level carried forward over the 3-bar entry window
    lvl_low = df["prev_low20"].where(sigL).ffill(limit=3)
    lvl_high = df["prev_high20"].where(sigS).ffill(limit=3)
    activeL = lvl_low.notna() & (~sigL)  # bars s+1..s+3 after signal bar s
    activeS = lvl_high.notna() & (~sigS)
    df["long_entry"] = (activeL & (df["c"] > lvl_low)).fillna(False)
    df["short_entry"] = (activeS & (df["c"] < lvl_high)).fillna(False)
    df["long_exit"] = pd.Series(False, index=df.index)
    df["short_exit"] = pd.Series(False, index=df.index)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
