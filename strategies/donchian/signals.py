"""Donchian breakout signals.

Long  when close > prior 20-bar high AND ADX(14) > 20  (trend regime)
Short when close < prior 20-bar low  AND ADX(14) > 20
Exit long  when close < prior 10-bar low
Exit short when close > prior 10-bar high
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    regime = df["adx"] > 20.0
    df["long_entry"] = (df["c"] > df["dc_high_entry"]) & regime
    df["short_entry"] = (df["c"] < df["dc_low_entry"]) & regime
    df["long_exit"] = df["c"] < df["dc_low_exit"]
    df["short_exit"] = df["c"] > df["dc_high_exit"]
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
