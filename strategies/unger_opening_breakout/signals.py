"""Unger opening-breakout signals.

Enter on the first 1h bar that CLOSES beyond the opening range (long above
range high, short below range low), one trade per side per day (masked in
indicators). Exits are all risk-level per Unger: no take-profit target --
let the breakout run -- with the 1.5xATR chandelier trail (trail_atr_mult)
doing the trade management, a 1.5xATR hard stop (the opposite range
extreme is the natural technical level; 1.5xATR is its ATR-scaled proxy),
and flat at session end via the 21-bar max hold.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = df["long_trigger"].fillna(False)
    df["short_entry"] = df["short_trigger"].fillna(False)
    df["long_exit"] = pd.Series(False, index=df.index)
    df["short_exit"] = pd.Series(False, index=df.index)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
