"""Gator Oscillator state-machine signals (Bill Williams).

Williams' four states describe the Alligator waking up and eating:

    awakes   -- one histogram flips green (eats now False, not sleeps)
    eats     -- both histograms green (gator_eats): the mouth is expanding
    fills out-- one histogram flips red again
    sleeps   -- both histograms red (gator_sleeps): the mouth is closed

Entries fire on the awakes -> eats transition *with a directional fan*:
the histograms say the Alligator is opening its mouth, and the fan
order says which way the mouth points. Expansion without a directional
fan is chop, not a trade.

    long_entry  = (eats & ~eats.shift(1)) & fan_bull
    short_entry = (eats & ~eats.shift(1)) & fan_bear

Exits: the position's job is to ride the expansion. Exit when the
Gator goes back to sleep (both histograms red) or the fan order flips
against the position:

    long_exit  = gator_sleeps | fan_bear
    short_exit = gator_sleeps | fan_bull

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    eats = df["gator_eats"].fillna(False).astype(bool)
    sleeps = df["gator_sleeps"].fillna(False).astype(bool)
    fan_bull = df["fan_bull"].fillna(False).astype(bool)
    fan_bear = df["fan_bear"].fillna(False).astype(bool)

    # awakes -> eats transition: both histograms flip to green together
    # (first valid bar counts as a transition; warmup excludes it).
    eats_flip = (eats & ~eats.shift(1).fillna(False)).fillna(False)

    df["long_entry"] = (eats_flip & fan_bull).fillna(False).astype(bool)
    df["short_entry"] = (eats_flip & fan_bear).fillna(False).astype(bool)
    df["long_exit"] = (sleeps | fan_bear).fillna(False).astype(bool)
    df["short_exit"] = (sleeps | fan_bull).fillna(False).astype(bool)
    return df
