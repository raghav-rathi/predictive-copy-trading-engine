"""Volume-confirmed breakout signals.

Long entry:  new 20-bar high AND volume > 1.5x trailing 20-bar mean.
Short entry: new 20-bar low AND volume > 1.5x trailing 20-bar mean.
Long exit:   close below the trailing 10-bar low (prior 10 bars).
Short exit:  close above the trailing 10-bar high (prior 10 bars).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = df["long_breakout"].fillna(False).astype(bool)
    df["short_entry"] = df["short_breakout"].fillna(False).astype(bool)
    df["long_exit"] = (
        (df["c"] < df["low_10_prev"]).fillna(False).astype(bool)
    )
    df["short_exit"] = (
        (df["c"] > df["high_10_prev"]).fillna(False).astype(bool)
    )
    return df
