"""Donchian + EMA filter signals.

Long entry:  close above the prior 20-bar high AND above EMA(50).
Short entry: close below the prior 20-bar low AND below EMA(50).
Long exit:   close below the prior 10-bar low (Turtle System 1 exit).
Short exit:  close above the prior 10-bar high.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = (
        (df["c"] > df["donchian_upper"]) & (df["c"] > df["ema_50"])
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        (df["c"] < df["donchian_lower"]) & (df["c"] < df["ema_50"])
    ).fillna(False).astype(bool)
    df["long_exit"] = (df["c"] < df["exit_low_10"]).fillna(False).astype(bool)
    df["short_exit"] = (df["c"] > df["exit_high_10"]).fillna(False).astype(bool)
    return df
