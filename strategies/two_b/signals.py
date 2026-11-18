"""Sperandeo 2B reversal signals.

Long entry:  the 2B-bottom failure close (close above the retest
             bar's high) — long_trigger.
Short entry: the 2B-top failure close (close below the retest bar's
             low) — short_trigger.
Long exit:   an opposite 2B-top signal OR a close below the 20-bar
             low extreme that armed the long (invalidation).
Short exit:  an opposite 2B-bottom signal OR a close above the
             20-bar high extreme that armed the short.

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
    df["long_exit"] = (short_trig | (df["c"] < df["last_bottom_extreme"])).fillna(False).astype(bool)
    df["short_exit"] = (long_trig | (df["c"] > df["last_top_extreme"])).fillna(False).astype(bool)
    return df
