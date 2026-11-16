"""Tom DeMark pivot breakout signals.

    long_entry  -- close breaks above the prior-day R1 and holds it
                   for 2 consecutive closes (fresh break: the close
                   2 bars ago was at or below its R1)
    short_entry -- close breaks below the prior-day S1 and holds it
                   for 2 consecutive closes (fresh break, mirrored)
    long_exit   -- close falls back inside the R1/S1 band (below R1),
                   or the low touches the opposite level S1
    short_exit  -- close rises back inside the band (above S1), or
                   the high touches the opposite level R1

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open). The 2-bar hold is measured
against each bar's own contemporaneous R1/S1, which roll hourly.
"""

import pandas as pd

HOLD_BARS = 2  # shipped default: consecutive closes beyond the level


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    r1 = df["demark_r1"]
    s1 = df["demark_s1"]
    above_r1 = (c > r1).fillna(False)
    below_s1 = (c < s1).fillna(False)
    df["long_entry"] = (
        above_r1
        & above_r1.shift(1).fillna(False)
        # Unknown 2 bars ago counts as "was above" -> no fresh break.
        & (~above_r1.shift(2).fillna(True))
    ).astype(bool)
    df["short_entry"] = (
        below_s1
        & below_s1.shift(1).fillna(False)
        & (~below_s1.shift(2).fillna(True))
    ).astype(bool)
    df["long_exit"] = (
        (c < r1).fillna(False) | (df["l"] <= s1).fillna(False)
    ).astype(bool)
    df["short_exit"] = (
        (c > s1).fillna(False) | (df["h"] >= r1).fillna(False)
    ).astype(bool)
    return df
