"""Judas swing signals.

Long entry:  the bullish-Judas structure shift (close above the
             highest high printed since the sweep bar, after a
             sweep below the Asian low and a reclaim close back
             above it) — long_trigger.
Short entry: the mirror — short_trigger.
Long exit:   an opposite bearish-Judas signal OR a close below the
             sweep low (invalidation).
Short exit:  an opposite bullish-Judas signal OR a close above the
             sweep high (invalidation).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
max hold 48 bars. Signal columns are boolean, no NaN, no lookahead
(the harness executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_trig = df["long_trigger"].fillna(False).astype(bool)
    short_trig = df["short_trigger"].fillna(False).astype(bool)
    df["long_entry"] = long_trig
    df["short_entry"] = short_trig
    df["long_exit"] = (short_trig | (df["c"] < df["last_bull_sweep_low"])).fillna(False).astype(bool)
    df["short_exit"] = (long_trig | (df["c"] > df["last_bear_sweep_high"])).fillna(False).astype(bool)
    return df
