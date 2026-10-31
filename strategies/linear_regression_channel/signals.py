"""Linear regression channel mean-reversion signals.

    long_entry  -- close crosses below the lower band
    short_entry -- close crosses above the upper band
    long_exit   -- close crosses above the midline
    short_exit  -- close crosses below the midline

State machine: entries only while flat; an exit may be followed by
an opposite entry on the same bar. Boolean columns, no NaN, no
lookahead (each bar's channel uses only closes through that bar).
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"]
    cross_dn = B.crossed_below(c, df["lr_lower"]).fillna(False).to_numpy(dtype=bool)
    cross_up = B.crossed_above(c, df["lr_upper"]).fillna(False).to_numpy(dtype=bool)
    cross_mid_up = B.crossed_above(c, df["lr_mid"]).fillna(False).to_numpy(dtype=bool)
    cross_mid_dn = B.crossed_below(c, df["lr_mid"]).fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None
    for i in range(n):
        if pos == "long" and cross_mid_up[i]:
            lx[i] = True
            pos = None
        elif pos == "short" and cross_mid_dn[i]:
            sx[i] = True
            pos = None
        if pos is None:
            if cross_dn[i]:
                le[i] = True
                pos = "long"
            elif cross_up[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
