"""Laguerre RSI signals.

Mean-reversion on the time-warped oscillator:
    long  on lrsi crossing UP through 0.2   (oversold reversal)
    short on lrsi crossing DOWN through 0.8 (overbought reversal)
    exit long  on cross below the 0.5 centerline
    exit short on cross above the 0.5 centerline
"""

import pandas as pd

OVERSOLD = 0.2
OVERBOUGHT = 0.8
CENTER = 0.5


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    r = df["lrsi"]
    prev = r.shift(1)
    df["long_entry"] = ((prev <= OVERSOLD) & (r > OVERSOLD)).fillna(False)
    df["short_entry"] = ((prev >= OVERBOUGHT) & (r < OVERBOUGHT)).fillna(False)
    df["long_exit"] = ((prev >= CENTER) & (r < CENTER)).fillna(False)
    df["short_exit"] = ((prev <= CENTER) & (r > CENTER)).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
