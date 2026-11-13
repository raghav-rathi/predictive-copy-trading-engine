"""GARCH(1,1) volatility-regime signals (Bollerslev, 1986).

Long entry:  close crosses above the previous 20-bar high AND
             forecast vol is inside the normal (30th-70th pct) band.
Short entry: close crosses below the previous 20-bar low AND
             forecast vol is inside the normal band.
Long exit:   close falls back below the previous 20-bar high
             (back inside the 20-bar range).
Short exit:  close rises back above the previous 20-bar low.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    from strategies import base as B

    long_entry = B.crossed_above(df["c"], df["prev_high_20"]) & df["vol_normal"].fillna(False)
    short_entry = B.crossed_below(df["c"], df["prev_low_20"]) & df["vol_normal"].fillna(False)
    long_exit = (df["c"] < df["prev_high_20"]).fillna(False)
    short_exit = (df["c"] > df["prev_low_20"]).fillna(False)
    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = long_exit.fillna(False).astype(bool)
    df["short_exit"] = short_exit.fillna(False).astype(bool)
    return df
