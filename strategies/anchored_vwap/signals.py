"""Anchored VWAP signals.

    long_entry  -- close crosses from below to above the AVWAP
                   anchored at the last swing low, while that
                   AVWAP is rising (vs 5 bars ago)
    short_entry -- mirror: close crosses from above to below
                   the AVWAP anchored at the last swing high,
                   while that AVWAP is falling
    long_exit   -- close crosses back below the swing-low AVWAP
    short_exit  -- close crosses back above the swing-high AVWAP

State machine: entries only while flat; an opposite cross
exits one side and may enter the other on the same bar.
Boolean columns, no NaN, no lookahead (all inputs causal).
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"]
    cross_up_low = B.crossed_above(c, df["avwap_low"]).to_numpy(dtype=bool)
    cross_dn_low = B.crossed_below(c, df["avwap_low"]).to_numpy(dtype=bool)
    cross_dn_high = B.crossed_below(c, df["avwap_high"]).to_numpy(dtype=bool)
    cross_up_high = B.crossed_above(c, df["avwap_high"]).to_numpy(dtype=bool)
    rising = df["avwap_low_rising"].to_numpy(dtype=bool)
    falling = df["avwap_high_falling"].to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and cross_dn_low[i]:
            lx[i] = True
            pos = None
        elif pos == "short" and cross_up_high[i]:
            sx[i] = True
            pos = None
        if pos is None:
            if cross_up_low[i] and rising[i]:
                le[i] = True
                pos = "long"
            elif cross_dn_high[i] and falling[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
