"""Renko 2-brick reversal signals (classic).

Trend = direction of the last 2 bricks. A reversal is 2 consecutive
bricks opposite to the prevailing trend:

    long_entry  = 2 up bricks complete while the run they reversed
                  was >= 3 down bricks (bullish 2-brick reversal
                  after a downtrend)
    short_entry = 2 down bricks complete while the run they reversed
                  was >= 3 up bricks

The "just completed" condition (run crosses 2 this bar) keeps the
signal to one bar per reversal -- a run that keeps extending does
not re-fire. Exits are the opposite 2-brick reversal: a long is
closed by a bearish 2-brick reversal, a short by a bullish one.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = df["renko_dir"]
    run = df["renko_run"]
    prev_run = df["renko_prev_run"]

    up_run = run.where(d == 1, 0)
    dn_run = run.where(d == -1, 0)

    # the 2nd brick of the new direction just printed this bar
    bull_reversal = (
        (d == 1)
        & (up_run >= 2)
        & (up_run.shift(1).fillna(0) < 2)
        & (prev_run >= 3)
    )
    bear_reversal = (
        (d == -1)
        & (dn_run >= 2)
        & (dn_run.shift(1).fillna(0) < 2)
        & (prev_run >= 3)
    )

    df["long_entry"] = bull_reversal.fillna(False).astype(bool)
    df["short_entry"] = bear_reversal.fillna(False).astype(bool)
    df["long_exit"] = bear_reversal.fillna(False).astype(bool)
    df["short_exit"] = bull_reversal.fillna(False).astype(bool)
    return df
