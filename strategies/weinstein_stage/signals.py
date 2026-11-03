"""Weinstein Stage Analysis signals.

Stan Weinstein stage analysis on 1h bars (adapted): Stage 2 long when close is above both EMA150 and EMA200 with EMA200 rising over 10 bars; Stage 4 short when close is below both with EMA200 falling. Entries on the first bar of each stage; exits on close crossing back through EMA150.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rising = (df["ema200"] > df["ema200"].shift(10)).fillna(False)
    falling = (df["ema200"] < df["ema200"].shift(10)).fillna(False)
    stage2 = (df["c"] > df["ema200"]) & (df["c"] > df["ema150"]) & rising
    stage4 = (df["c"] < df["ema200"]) & (df["c"] < df["ema150"]) & falling
    prev2 = stage2.shift(1).fillna(False)
    prev4 = stage4.shift(1).fillna(False)
    df["long_entry"] = (stage2 & ~prev2).astype(bool)
    df["short_entry"] = (stage4 & ~prev4).astype(bool)
    df["long_exit"] = (df["c"] < df["ema150"]).fillna(False).astype(bool)
    df["short_exit"] = (df["c"] > df["ema150"]).fillna(False).astype(bool)
    return df
