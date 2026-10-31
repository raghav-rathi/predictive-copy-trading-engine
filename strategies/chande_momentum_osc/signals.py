"""Chande Momentum Oscillator threshold signals.

    long_entry  -- CMO crosses above -50 (leaving oversold)
    short_entry -- CMO crosses below +50 (leaving overbought)
    long_exit   -- CMO crosses below 0 or crosses above +50
    short_exit  -- CMO crosses above 0 or crosses below -50

State machine: entries only while flat; an exit may re-enter the other
side on the same bar. Boolean columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.chande_momentum_osc.indicators import OVERBOUGHT, OVERSOLD


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    cmo = df["cmo"]
    up_from_oversold = (
        B.crossed_above(cmo, OVERSOLD).fillna(False).to_numpy(dtype=bool)
    )
    down_from_overbought = (
        B.crossed_below(cmo, OVERBOUGHT).fillna(False).to_numpy(dtype=bool)
    )
    cross_below_zero = (
        B.crossed_below(cmo, 0.0).fillna(False).to_numpy(dtype=bool)
    )
    cross_above_zero = (
        B.crossed_above(cmo, 0.0).fillna(False).to_numpy(dtype=bool)
    )
    cross_above_ob = (
        B.crossed_above(cmo, OVERBOUGHT).fillna(False).to_numpy(dtype=bool)
    )
    cross_below_os = (
        B.crossed_below(cmo, OVERSOLD).fillna(False).to_numpy(dtype=bool)
    )

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and (cross_below_zero[i] or cross_above_ob[i]):
            lx[i] = True
            pos = None
        elif pos == "short" and (cross_above_zero[i] or cross_below_os[i]):
            sx[i] = True
            pos = None
        if pos is None:
            if up_from_oversold[i]:
                le[i] = True
                pos = "long"
            elif down_from_overbought[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
