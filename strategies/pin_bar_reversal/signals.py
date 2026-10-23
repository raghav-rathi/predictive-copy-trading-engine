"""Pin bar reversal signals — enter on the rejection, exit on the opposite.

The pin bar IS the entry trigger: a bullish pin (long rejection tail
down at a 5-bar swing low) buys; a bearish pin (long rejection tail
up at a 5-bar swing high) sells.  Exits are the opposite rejection —
a bearish pin ends a long, a bullish pin ends a short — plus the
ATR stop / 2R target / 48-bar max hold in risk.py.

    long_entry  = bullish_pin
    short_entry = bearish_pin
    long_exit   = bearish_pin
    short_exit  = bullish_pin

A single bar is almost never both a bullish and a bearish pin at
once (the tail would have to be >= 2/3 of the range on both sides),
so entries and exits are naturally mutually exclusive.  The signal
on bar i uses data through bar i's close only; the harness executes
at bar i+1's open.

Signal columns are boolean, no NaN, no lookahead.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bull = df["bullish_pin"].fillna(False).astype(bool)
    bear = df["bearish_pin"].fillna(False).astype(bool)
    df["long_entry"] = bull
    df["short_entry"] = bear
    df["long_exit"] = bear
    df["short_exit"] = bull
    return df
