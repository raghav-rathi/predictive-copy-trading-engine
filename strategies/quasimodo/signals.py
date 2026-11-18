"""Quasimodo signals.

Long entry:  the bullish-QM entry close (close above the
             retracement leg's swing high RH) — long_trigger.
Short entry: the bearish-QM entry close (close below the
             retracement leg's swing low RL) — short_trigger.
Long exit:   an opposite bearish-QM signal OR a close below the
             bullish head low (invalidation).
Short exit:  an opposite bullish-QM signal OR a close above the
             bearish head high (invalidation).

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
    df["long_exit"] = (short_trig | (df["c"] < df["last_bull_head_low"])).fillna(False).astype(bool)
    df["short_exit"] = (long_trig | (df["c"] > df["last_bear_head_high"])).fillna(False).astype(bool)
    return df
