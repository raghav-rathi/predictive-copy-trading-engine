"""Balanced Price Range signals.

Long entry:  the first close inside an active bullish BPR zone
             after price had closed above the zone (a return into
             it) — long_trigger.
Short entry: the mirror on a bearish BPR — short_trigger.
Long exit:   an opposite bearish-BPR signal OR a close below the
             bullish zone's bottom (invalidation).
Short exit:  an opposite bullish-BPR signal OR a close above the
             bearish zone's top (invalidation).

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
    df["long_exit"] = (short_trig | (df["c"] < df["bull_bpr_bottom"])).fillna(False).astype(bool)
    df["short_exit"] = (long_trig | (df["c"] > df["bear_bpr_top"])).fillna(False).astype(bool)
    return df
