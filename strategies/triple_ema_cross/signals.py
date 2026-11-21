"""Triple EMA Crossover signals.

Long entry:  EMA(5) crosses up through EMA(13) AND
               EMA5 > EMA13 > EMA50 on that bar (transition only).
Short entry: EMA(5) crosses down through EMA(13) AND
               EMA5 < EMA13 < EMA50 on that bar (transition only).
Long exit:   EMA(5) crosses down through EMA(13).
Short exit:  EMA(5) crosses up through EMA(13).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    f = df["ema_fast"]
    m = df["ema_mid"]
    s = df["ema_slow"]
    prev_f = f.shift(1)
    prev_m = m.shift(1)
    cross_up = ((f > m) & (prev_f <= prev_m)).fillna(False)
    cross_dn = ((f < m) & (prev_f >= prev_m)).fillna(False)
    df["long_entry"] = (
        cross_up & (f > m) & (m > s)).fillna(False).astype(bool)
    df["short_entry"] = (
        cross_dn & (f < m) & (m < s)).fillna(False).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
