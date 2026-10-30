"""Multi-timeframe stack signals.

    long_entry  -- 1h EMA(9) crosses above EMA(21) while 4h trend is up
    short_entry -- 1h EMA(9) crosses below EMA(21) while 4h trend is down
    long_exit   -- opposite 1h cross (EMA(9) below EMA(21))
    short_exit  -- opposite 1h cross (EMA(9) above EMA(21))

State machine: entries only while flat and only with the 4h trend;
an opposite cross exits and may re-enter the other side on the same
bar if the trend agrees. Boolean columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    cross_up = B.crossed_above(df["ema9"], df["ema21"]).fillna(False).to_numpy(dtype=bool)
    cross_down = B.crossed_below(df["ema9"], df["ema21"]).fillna(False).to_numpy(dtype=bool)
    trend = df["htf_trend"].to_numpy(dtype=int)

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
            if cross_up[i] and trend[i] == 1:
                le[i] = True
                pos = "long"
            elif cross_down[i] and trend[i] == -1:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
