"""Aroon cross signals.

    long_entry  -- Aroon Up crosses above Aroon Down while Aroon Up > 70
    short_entry -- Aroon Down crosses above Aroon Up while Aroon Down > 70
    long_exit   -- Aroon Down crosses above Aroon Up (opposite cross)
    short_exit  -- Aroon Up crosses above Aroon Down (opposite cross)

The > 70 gate applies to entries only: the crossing line must
be making fresh extremes (a high/low within the last ~7 bars
of the 25-bar window), not merely drifting past a flat line.
Exits take the opposite cross unconditionally. NaN comparisons
are False, so no signal fires before both Aroon lines exist.
Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies import base as B

STRONG = 70.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = df["aroon_up"]
    down = df["aroon_down"]
    cross_up = B.crossed_above(up, down)
    cross_down = B.crossed_below(up, down)
    df["long_entry"] = (
        cross_up & (up > STRONG)
    ).fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = (
        cross_down & (down > STRONG)
    ).fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = cross_down.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = cross_up.fillna(False).to_numpy(dtype=bool)
    return df
