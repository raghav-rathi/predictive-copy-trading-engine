"""Weinstein Stage Analysis indicators.

Stan Weinstein stage analysis on 1h bars (adapted): Stage 2 long when close is above both EMA150 and EMA200 with EMA200 rising over 10 bars; Stage 4 short when close is below both with EMA200 falling. Entries on the first bar of each stage; exits on close crossing back through EMA150.
"""

import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema50"] = B.ema(df["c"], 50)
    df["ema150"] = B.ema(df["c"], 150)
    df["ema200"] = B.ema(df["c"], 200)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
