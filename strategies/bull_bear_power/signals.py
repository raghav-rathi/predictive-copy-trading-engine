"""Bull Power / Bear Power signals (Alexander Elder, 1993).

Long entry:  Bear Power turns up (rising vs the prior bar) while
             still below zero AND Bull Power is above zero (sellers
             losing strength, buyers still in control).
Short entry: Bull Power turns down (falling vs the prior bar) while
             still above zero AND Bear Power is below zero.
Long exit:   the opposite turn (the short-entry condition).
Short exit:  the opposite turn (the long-entry condition).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies, so
in practice most positions end on the stop/trail/max-hold before the
opposite turn; the opposite turn is the system-defined exit.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bull = df["bull_power"]
    bear = df["bear_power"]
    bear_rising = (bear > bear.shift(1)).fillna(False)
    bull_falling = (bull < bull.shift(1)).fillna(False)
    long_cond = bear_rising & (bear < 0) & (bull > 0)
    short_cond = bull_falling & (bull > 0) & (bear < 0)
    df["long_entry"] = long_cond.fillna(False).astype(bool)
    df["short_entry"] = short_cond.fillna(False).astype(bool)
    df["long_exit"] = short_cond.fillna(False).astype(bool)
    df["short_exit"] = long_cond.fillna(False).astype(bool)
    return df
