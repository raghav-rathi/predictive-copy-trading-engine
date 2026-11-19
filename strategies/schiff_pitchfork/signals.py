"""Schiff pitchfork signals.

Long entry:  price touches the bullish Schiff median line from
             above (low within 0.5 ATR(14) of the line) and closes
             back above it (long_trigger).
Short entry: the mirror — price touches the bearish Schiff median
             line from below and closes back below it
             (short_trigger).
Long exit:   an opposite short signal OR a close below the lower
             parallel (the parallel through C).
Short exit:  an opposite long signal OR a close above the upper
             parallel (the parallel through C).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_trig = df["long_trigger"].fillna(False).astype(bool)
    short_trig = df["short_trigger"].fillna(False).astype(bool)
    df["long_entry"] = long_trig
    df["short_entry"] = short_trig
    df["long_exit"] = (short_trig | (df["c"] < df["pf_bull_lower"])).fillna(False).astype(bool)
    df["short_exit"] = (long_trig | (df["c"] > df["pf_bear_upper"])).fillna(False).astype(bool)
    return df
