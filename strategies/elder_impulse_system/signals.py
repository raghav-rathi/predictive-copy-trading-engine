"""Elder Impulse System signals.

Long on the first green bar after a red/blue bar; short on the first red
bar after a green/blue bar. Exit long on a red or blue bar; exit short on
a green or blue bar. Signals use only data through bar i's close.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    green = df["impulse_green"].fillna(False)
    red = df["impulse_red"].fillna(False)
    prev_green = green.shift(1).fillna(False)
    prev_red = red.shift(1).fillna(False)
    df["long_entry"] = (green & ~prev_green).astype(bool)
    df["short_entry"] = (red & ~prev_red).astype(bool)
    df["long_exit"] = (~green).astype(bool)
    df["short_exit"] = (~red).astype(bool)
    return df
