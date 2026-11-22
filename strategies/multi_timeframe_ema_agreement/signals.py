"""Multi-Timeframe EMA Agreement signals (BotLab study).

Base entry is a 1h EMA(9)/EMA(21) cross. The BotLab filter — the
only one of 12 filters x 5 datasets (60 combinations) to clear
the multiple-testing bar (t ~ 2.86) — gates the cross on
higher-timeframe agreement:

    LONG  only when EMA(9) crosses ABOVE EMA(21) on 1h
          AND the 4h EMA(9) > 4h EMA(21) (4h pair agrees).
    SHORT only when EMA(9) crosses BELOW EMA(21) on 1h
          AND the 4h EMA(9) < 4h EMA(21).

Exit on the opposite 1h cross (the 4h filter is an entry gate
only, as in the study). A one-position state machine gates
entries to flat bars; the harness executes at the next bar's
open. All conditions read bars <= i; the 4h EMAs only ever
reflect completed 4h bars (see indicators.py).
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    fast1 = df["ema_fast_1h"]
    slow1 = df["ema_slow_1h"]
    fast4 = df["ema_fast_4h"]
    slow4 = df["ema_slow_4h"]

    cross_up = B.crossed_above(fast1, slow1).fillna(False).to_numpy(dtype=bool)
    cross_dn = B.crossed_below(fast1, slow1).fillna(False).to_numpy(dtype=bool)
    htf_long = (fast4 > slow4).fillna(False).to_numpy(dtype=bool)
    htf_short = (fast4 < slow4).fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" | "short" | None
    for i in range(n):
        if pos == "long" and cross_dn[i]:
            lx[i] = True
            pos = None
        elif pos == "short" and cross_up[i]:
            sx[i] = True
            pos = None
        if pos is None:
            if cross_up[i] and htf_long[i]:
                le[i] = True
                pos = "long"
            elif cross_dn[i] and htf_short[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
