"""Fair Value Gap indicators (SMC / ICT).

A bullish FVG forms when bar i's low clears bar (i-2)'s high: the zone
between those two levels traded thinly during the displacement leg.
A bearish FVG is the mirror image. This module tracks only the most
recent unfilled gap per side; a gap is filled (and dropped) once price
closes through its far side, and gaps older than 200 bars are dropped
as stale.

Columns:
    bull_gap_top / bull_gap_bottom -- most recent open bullish gap
    bull_gap_age -- bars since the bullish gap formed (0 on its bar)
    bear_gap_top / bear_gap_bottom -- most recent open bearish gap
    bear_gap_age -- bars since the bearish gap formed
    atr -- Wilder ATR(14) for the risk layer

State is built bar by bar using only bars up to and including the
current bar, so the indicators are strictly causal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

MAX_AGE_BARS = 200


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    bull_top = np.full(n, np.nan)
    bull_bot = np.full(n, np.nan)
    bull_age = np.full(n, np.nan)
    bear_top = np.full(n, np.nan)
    bear_bot = np.full(n, np.nan)
    bear_age = np.full(n, np.nan)
    bull = None  # (bottom, top, birth_bar)
    bear = None
    for i in range(n):
        if i >= 2:
            if l[i] > h[i - 2]:
                bull = (h[i - 2], l[i], i)
            if h[i] < l[i - 2]:
                bear = (h[i], l[i - 2], i)
        if bull is not None:
            if c[i] < bull[0] or i - bull[2] > MAX_AGE_BARS:
                bull = None
        if bear is not None:
            if c[i] > bear[1] or i - bear[2] > MAX_AGE_BARS:
                bear = None
        if bull is not None:
            bull_bot[i], bull_top[i] = bull[0], bull[1]
            bull_age[i] = i - bull[2]
        if bear is not None:
            bear_bot[i], bear_top[i] = bear[0], bear[1]
            bear_age[i] = i - bear[2]
    df["bull_gap_top"] = bull_top
    df["bull_gap_bottom"] = bull_bot
    df["bull_gap_age"] = bull_age
    df["bear_gap_top"] = bear_top
    df["bear_gap_bottom"] = bear_bot
    df["bear_gap_age"] = bear_age
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
