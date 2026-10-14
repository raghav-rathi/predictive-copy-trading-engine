"""Awesome Oscillator signals (Bill Williams, "Trading Chaos").

Entries (any one fires):
  a) zero-line cross: long when AO crosses above 0, short when below 0;
  b) saucer: three bars on one side of zero with the middle bar the
     extremum and the last bar turning back toward the line;
  c) twin peaks: second extremum closer to zero than the first, AO never
     crossing zero between them, AO turning back toward the line.
Exits: the opposite zero-line cross (longs exit on cross below 0, shorts
on cross above 0). Risk-level exits (stop, max hold) come from risk.py.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ao = df["ao"]
    prev = ao.shift(1)
    cross_up = ((prev <= 0) & (ao > 0)).fillna(False)
    cross_dn = ((prev >= 0) & (ao < 0)).fillna(False)
    df["long_entry"] = (
        cross_up | df["bull_saucer"] | df["bull_twin_peaks"]
    ).fillna(False)
    df["short_entry"] = (
        cross_dn | df["bear_saucer"] | df["bear_twin_peaks"]
    ).fillna(False)
    df["long_exit"] = cross_dn
    df["short_exit"] = cross_up
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
