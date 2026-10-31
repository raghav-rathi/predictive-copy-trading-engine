"""Efficiency Ratio filter gating an EMA cross.

    long_entry  -- EMA(9) crosses above EMA(21) while ER(10) > 0.3
    short_entry -- EMA(9) crosses below EMA(21) while ER(10) > 0.3
    long_exit   -- opposite EMA cross (no ER condition on exits)
    short_exit  -- opposite EMA cross (no ER condition on exits)

State machine: entries only while flat; an opposite cross exits and
may re-enter the other side on the same bar. Boolean columns, no NaN,
no lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.efficiency_ratio.indicators import ER_THRESHOLD


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    cross_up = (
        B.crossed_above(df["ema9"], df["ema21"])
        .fillna(False)
        .to_numpy(dtype=bool)
    )
    cross_down = (
        B.crossed_below(df["ema9"], df["ema21"])
        .fillna(False)
        .to_numpy(dtype=bool)
    )
    efficient = (df["er"] > ER_THRESHOLD).fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and cross_down[i]:
            lx[i] = True
            pos = None
        elif pos == "short" and cross_up[i]:
            sx[i] = True
            pos = None
        if pos is None:
            if cross_up[i] and efficient[i]:
                le[i] = True
                pos = "long"
            elif cross_down[i] and efficient[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
