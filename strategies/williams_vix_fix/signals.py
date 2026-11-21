"""Williams VIX Fix signals.

Long entry:  green flash on this bar AND NOT on the previous bar
              (transition only).
Short entry: inverted flash on this bar AND NOT on the previous bar
              (transition only).
Long exit:   inverted flash (any bar).
Short exit:  green flash (any bar).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    green = df["green_flash"].fillna(False).astype(bool)
    prev_green = green.shift(1).fillna(False).astype(bool)
    inv = df["inv_flash"].fillna(False).astype(bool)
    prev_inv = inv.shift(1).fillna(False).astype(bool)
    df["long_entry"] = (green & ~prev_green).fillna(False).astype(bool)
    df["short_entry"] = (inv & ~prev_inv).fillna(False).astype(bool)
    df["long_exit"] = inv.fillna(False).astype(bool)
    df["short_exit"] = green.fillna(False).astype(bool)
    return df
