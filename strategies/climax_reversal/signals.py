"""Wyckoff climax reversal signals.

Long entry:  selling climax (new 20-bar low, volume > 2x mean,
             close in the upper third of the bar).
Short entry: buying climax (new 20-bar high, volume > 2x mean,
             close in the lower third of the bar).
Long exit:   opposite climax (buying climax).
Short exit:  opposite climax (selling climax).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry = df["selling_climax"].fillna(False).astype(bool)
    short_entry = df["buying_climax"].fillna(False).astype(bool)
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = short_entry
    df["short_exit"] = long_entry
    return df
