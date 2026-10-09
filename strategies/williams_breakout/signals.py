"""Williams breakout signals.

Long  when close > prior 24-bar high AND 24-bar range is expanded
Short when close < prior 24-bar low  AND 24-bar range is expanded
Exits come from the risk layer (ATR target / stop / max hold) — the
breakout has no natural signal exit.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    valid = df["hi_24"].notna() & df["range_expanded"].notna()
    df["long_entry"] = (df["c"] > df["hi_24"]) & df["range_expanded"].fillna(False) & valid
    df["short_entry"] = (df["c"] < df["lo_24"]) & df["range_expanded"].fillna(False) & valid
    df["long_exit"] = False
    df["short_exit"] = False
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
