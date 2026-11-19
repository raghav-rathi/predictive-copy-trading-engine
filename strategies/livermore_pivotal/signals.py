"""Livermore pivotal-point signals.

Long entry:  the resumption close — a close above the natural
             reaction's high on expanding volume (long_trigger).
Short entry: the mirror — a close below the natural reaction's
             low on expanding volume (short_trigger).
Long exit:   an opposite short signal OR a close back below the
             bull pivot (Livermore's danger signal).
Short exit:  an opposite long signal OR a close back above the
             bear pivot.

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
    df["long_exit"] = (short_trig | (df["c"] < df["bull_pivot"])).fillna(False).astype(bool)
    df["short_exit"] = (long_trig | (df["c"] > df["bear_pivot"])).fillna(False).astype(bool)
    return df
