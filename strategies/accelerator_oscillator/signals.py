"""Williams' Accelerator Oscillator bar-count entry/exit rules.

With the driving force (trade in the direction the force points):

    long_entry  = (ac > 0) & (last 2 bars green)
    short_entry = (ac < 0) & (last 2 bars red)

Against the driving force (counter-trend, needs stronger confirmation):

    long_entry  = (ac < 0) & (last 3 bars green)
    short_entry = (ac > 0) & (last 3 bars red)

Williams' rule of thumb: "you can not buy when the current column is
red, and you can not sell when the current column is green." The zero
line itself never generates a signal alone -- a sign change without
the required consecutive color run is not an entry.

Exits: the opposite entry condition, or the color flipping against
the position for 2 consecutive bars (the acceleration that justified
the trade has reversed):

    long_exit   = short_entry | (last 2 bars red)
    short_exit  = long_entry  | (last 2 bars green)

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd


def _runs(green: pd.Series, n: int) -> pd.Series:
    """True where the last n bars (including the current bar) are green."""
    g = green.astype(int).fillna(0)
    run = g.copy()
    for k in range(1, n):
        run = run + g.shift(k).fillna(0)
    return (run >= n)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ac = df["ac"]
    green = df["ac_green"].fillna(False).astype(bool)
    red = df["ac_red"].fillna(False).astype(bool)

    green2 = _runs(green, 2)
    green3 = _runs(green, 3)
    red2 = _runs(red, 2)
    red3 = _runs(red, 3)

    above = (ac > 0).fillna(False)
    below = (ac < 0).fillna(False)

    long_entry = ((above & green2) | (below & green3)).fillna(False).astype(bool)
    short_entry = ((below & red2) | (above & red3)).fillna(False).astype(bool)

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    # Exits: opposite entry condition, or 2 consecutive bars of the
    # color against the position.
    df["long_exit"] = (short_entry | red2).fillna(False).astype(bool)
    df["short_exit"] = (long_entry | green2).fillna(False).astype(bool)
    return df
