"""Ultimate Oscillator indicators (Williams).

Plain-English idea: buying pressure is how much of today's range the
close captured above the prior close (or the low). Averaging that
pressure over 7, 14 and 28 bars — with the shortest window weighted
most — gives one momentum number that reacts fast but doesn't whipsaw
like a single short average. Williams' use of it was divergence:
when price makes a new extreme but the oscillator refuses to, the
trend is running out of buyers/sellers.

Mechanics:
  bp  = c - min(l, prev_c)
  tr  = max(h, prev_c) - min(l, prev_c)
  avgN = sum(bp, N) / sum(tr, N)   for N in (7, 14, 28)
  UO  = 100 * (4*avg7 + 2*avg14 + avg28) / 7, clipped to [0, 100]

No lookahead: rolling sums and shifts use only bars through i.
"""

import numpy as np
import pandas as pd

from strategies import base as B

W1, W2, W3 = 7, 14, 28


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_c = df["c"].shift(1)
    low_ref = pd.concat([df["l"], prev_c], axis=1).min(axis=1)
    high_ref = pd.concat([df["h"], prev_c], axis=1).max(axis=1)
    bp = df["c"] - low_ref
    tr = high_ref - low_ref

    def _avg(n):
        return bp.rolling(n, min_periods=n).sum() / tr.rolling(n, min_periods=n).sum()

    avg7, avg14, avg28 = _avg(W1), _avg(W2), _avg(W3)
    uo = 100.0 * (4.0 * avg7 + 2.0 * avg14 + avg28) / 7.0
    df["uo"] = uo.clip(0.0, 100.0)
    df["uo_avg7"] = avg7
    df["uo_avg14"] = avg14
    df["uo_avg28"] = avg28
    return df
