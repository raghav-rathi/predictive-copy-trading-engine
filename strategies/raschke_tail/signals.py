"""Raschke Tail signals — buy-stop / sell-stop approximation.

A tail bar sets a trigger level (its high for a bullish tail, its low
for a bearish tail). The entry fires on the first bar within
``window`` bars after the tail whose high (long) exceeds the tail bar's
high or whose low (short) undercuts the tail bar's low. The tail bar
itself never triggers. No lookahead: trigger levels come from earlier
bars via forward-fill, evaluated against bar i's own high/low.
"""

import pandas as pd


def add_signals(df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
    df = df.copy()
    trig_high = df["h"].where(df["bullish_tail"]).ffill(limit=window)
    trig_low = df["l"].where(df["bearish_tail"]).ffill(limit=window)

    df["long_entry"] = (df["h"] > trig_high).fillna(False).astype(bool)
    df["short_entry"] = (df["l"] < trig_low).fillna(False).astype(bool)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
