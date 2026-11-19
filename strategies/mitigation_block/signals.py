"""Mitigation block signals.

Long entry:  the first close inside an armed bullish mitigation
             block (a return into it after the structure break) —
             long_trigger.
Short entry: the mirror on a bearish block — short_trigger.
Long exit:   an opposite bearish-block signal OR a close below the
             bullish block's low.
Short exit:  an opposite bullish-block signal OR a close above the
             bearish block's high.

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
    df["long_exit"] = (short_trig | (df["c"] < df["bull_block_bottom"])).fillna(False).astype(bool)
    df["short_exit"] = (long_trig | (df["c"] > df["bear_block_top"])).fillna(False).astype(bool)
    return df
