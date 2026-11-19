"""SMT divergence signals.

Long entry:  the bullish-SMT structure shift (first close above the
             traded coin's prior swing high after a bullish SMT
             divergence armed) — long_trigger.
Short entry: the mirror — short_trigger.
Long exit:   an opposite bearish-SMT signal OR a close below the
             divergence swing low (invalidation).
Short exit:  an opposite bullish-SMT signal OR a close above the
             divergence swing high (invalidation).

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
    df["long_exit"] = (short_trig | (df["c"] < df["last_bull_div_low"])).fillna(False).astype(bool)
    df["short_exit"] = (long_trig | (df["c"] > df["last_bear_div_high"])).fillna(False).astype(bool)
    return df
