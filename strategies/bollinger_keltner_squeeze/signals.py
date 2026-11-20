"""Bollinger/Keltner squeeze signals.

Fire = the first bar the squeeze turns OFF after being ON.
Long entry:  fire with momentum > 0.
Short entry: fire with momentum < 0.
Long exit:   opposite (short) signal.
Short exit:  opposite (long) signal.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sq = df["squeeze_on"].fillna(False).astype(bool)
    prev = sq.shift(1).fillna(False).astype(bool)
    fire = (~sq) & prev
    mom = df["momentum"]
    df["long_entry"] = (fire & (mom > 0)).fillna(False).astype(bool)
    df["short_entry"] = (fire & (mom < 0)).fillna(False).astype(bool)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
