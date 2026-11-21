"""On-Balance Volume Breakout signals.

Long entry:  OBV closes above its prior-20-bar high
               (transition only — the previous bar's OBV was NOT
               above the then-current prior-20-bar high).
Short entry: OBV closes below its prior-20-bar low
               (transition only).
Long exit:   OBV closes below its prior-20-bar low.
Short exit:  OBV closes above its prior-20-bar high.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    obv = df["obv"]
    hi = df["obv_high"]
    lo = df["obv_low"]
    prev_obv = obv.shift(1)
    prev_hi = hi.shift(1)
    prev_lo = lo.shift(1)
    df["long_entry"] = (
        (obv > hi) & (prev_obv <= prev_hi)).fillna(False).astype(bool)
    df["short_entry"] = (
        (obv < lo) & (prev_obv >= prev_lo)).fillna(False).astype(bool)
    df["long_exit"] = (obv < lo).fillna(False).astype(bool)
    df["short_exit"] = (obv > hi).fillna(False).astype(bool)
    return df
