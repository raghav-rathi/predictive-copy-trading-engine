"""DMI cross signals.

    long_entry  -- +DI crosses above -DI while ADX(14) > 20
    short_entry -- -DI crosses above +DI while ADX(14) > 20
    long_exit   -- -DI crosses above +DI (the opposite DI cross)
    short_exit  -- +DI crosses above -DI (the opposite DI cross)

The ADX > 20 gate applies to entries only: an exit on the
opposite cross is taken even if ADX has fallen back below 20,
because a crossed DI pair no longer supports the open side.
NaN comparisons are False, so no signal fires before +DI/-DI
and ADX exist. Boolean columns, no NaN, no lookahead (a cross
on bar i uses only data through bar i's close; the harness
executes at bar i+1's open).
"""

import pandas as pd

from strategies import base as B

ADX_MIN = 20.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    plus = df["plus_di"]
    minus = df["minus_di"]
    adx = df["adx"]
    cross_up = B.crossed_above(plus, minus)
    cross_down = B.crossed_below(plus, minus)
    strong = (adx > ADX_MIN).fillna(False)
    df["long_entry"] = (cross_up & strong).fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = (cross_down & strong).fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = cross_down.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = cross_up.fillna(False).to_numpy(dtype=bool)
    return df
