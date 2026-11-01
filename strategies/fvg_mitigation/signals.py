"""FVG mitigation signals.

    long_entry  -- first bar whose low dips into the open bullish gap
                  while the close still holds above the gap bottom
    short_entry -- first bar whose high pokes into the open bearish gap
                  while the close still holds below the gap top
    long_exit   -- close below the open bullish gap's bottom (filled
                  through: the mitigation thesis failed)
    short_exit  -- close above the open bearish gap's top

A gap is used once: after an entry fires, that gap no longer generates
entries until a fresh gap forms. Entries never fire on the gap's own
formation bar (its low IS the gap top by construction); only bars with
gap age >= 1 can enter. Boolean columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    l = df["l"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    btop = df["bull_gap_top"].to_numpy(dtype=float)
    bbot = df["bull_gap_bottom"].to_numpy(dtype=float)
    bage = df["bull_gap_age"].to_numpy(dtype=float)
    btop_b = df["bear_gap_top"].to_numpy(dtype=float)
    bbot_b = df["bear_gap_bottom"].to_numpy(dtype=float)
    bage_b = df["bear_gap_age"].to_numpy(dtype=float)
    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)
    bull_used = True
    bear_used = True
    prev_bull = None
    prev_bear = None
    for i in range(n):
        bull = None if np.isnan(btop[i]) else (bbot[i], btop[i])
        bear = None if np.isnan(btop_b[i]) else (bbot_b[i], btop_b[i])
        if bull != prev_bull:
            bull_used = False
        if bear != prev_bear:
            bear_used = False
        prev_bull, prev_bear = bull, bear
        if bull is not None and not bull_used and bage[i] >= 1:
            if l[i] <= bull[1] and c[i] >= bull[0]:
                le[i] = True
                bull_used = True
        if bear is not None and not bear_used and bage_b[i] >= 1:
            if h[i] >= bear[0] and c[i] <= bear[1]:
                se[i] = True
                bear_used = True
        if bull is not None and c[i] < bull[0]:
            lx[i] = True
        if bear is not None and c[i] > bear[1]:
            sx[i] = True
    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
