"""Choppiness Index regime filter + Donchian breakout signals.

    long_entry  -- CHOP < 38.2 (trending regime) and close crosses above
                   the prior Donchian(20) high
    short_entry -- CHOP < 38.2 and close crosses below the prior
                   Donchian(20) low
    long_exit   -- CHOP crosses above 61.8 (regime turns choppy) or close
                   crosses below the prior Donchian low
    short_exit  -- CHOP crosses above 61.8 or close crosses above the
                   prior Donchian high

State machine: entries only while flat; an exit may re-enter the other
side on the same bar. Boolean columns, no NaN, no lookahead (the
Donchian bands already exclude the current bar).
"""

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.choppiness_index.indicators import (
    CHOPPY_LEVEL,
    TREND_LEVEL,
)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    chop = df["chop"]
    trending = (chop < TREND_LEVEL).fillna(False).to_numpy(dtype=bool)
    chop_turns_choppy = (
        B.crossed_above(chop, CHOPPY_LEVEL).fillna(False).to_numpy(dtype=bool)
    )
    cross_up = (
        B.crossed_above(df["c"], df["donchian_high"])
        .fillna(False)
        .to_numpy(dtype=bool)
    )
    cross_down = (
        B.crossed_below(df["c"], df["donchian_low"])
        .fillna(False)
        .to_numpy(dtype=bool)
    )

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and (chop_turns_choppy[i] or cross_down[i]):
            lx[i] = True
            pos = None
        elif pos == "short" and (chop_turns_choppy[i] or cross_up[i]):
            sx[i] = True
            pos = None
        if pos is None:
            if trending[i] and cross_up[i]:
                le[i] = True
                pos = "long"
            elif trending[i] and cross_down[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
