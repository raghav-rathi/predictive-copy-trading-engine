"""Market-structure indicators (SMC break-of-structure / change-of-character).

Swing pivots: fractal swing high at bar i iff h[i] is the strict maximum
of h[i-LEFT..i+RIGHT] (mirror for lows), LEFT=RIGHT=2. Walking forward:
a bullish BOS fires when close > last confirmed swing high; a bearish
BOS when close < last confirmed swing low. Direction state: +1 after a
bullish BOS, -1 after a bearish BOS; a BOS against the prevailing
direction is a CHoCH. The pivot needs RIGHT bars to confirm, so the
swing level lags RIGHT bars -- causal by construction.
"""

import numpy as np
import pandas as pd

LEFT = 2
RIGHT = 2


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy()
    c = df["c"].to_numpy()
    l = df["l"].to_numpy()
    n = len(df)

    is_sh = np.zeros(n, dtype=bool)
    is_sl = np.zeros(n, dtype=bool)
    for i in range(LEFT, n - RIGHT):
        w = h[i - LEFT : i + RIGHT + 1]
        if w.argmax() == LEFT:  # strict-ish local max; ties resolve to first
            is_sh[i] = True
        wl = l[i - LEFT : i + RIGHT + 1]
        if wl.argmin() == LEFT:
            is_sl[i] = True

    bos_up = np.zeros(n, dtype=bool)
    bos_dn = np.zeros(n, dtype=bool)
    choch_up = np.zeros(n, dtype=bool)
    choch_dn = np.zeros(n, dtype=bool)
    direction = np.full(n, np.nan)
    last_sh = np.nan
    last_sl = np.nan
    d = 0.0
    for i in range(n):
        # pivots confirm RIGHT bars late: only use pivots confirmed by bar i
        j = i - RIGHT
        if j >= 0:
            if is_sh[j]:
                last_sh = h[j]
            if is_sl[j]:
                last_sl = l[j]
        if not np.isnan(last_sh) and c[i] > last_sh:
            bos_up[i] = True
            if d == -1.0:
                choch_up[i] = True
            d = 1.0
            last_sh = np.nan  # level consumed; wait for the next pivot
        elif not np.isnan(last_sl) and c[i] < last_sl:
            bos_dn[i] = True
            if d == 1.0:
                choch_dn[i] = True
            d = -1.0
            last_sl = np.nan
        direction[i] = d

    df["swing_high"] = is_sh
    df["swing_low"] = is_sl
    df["bos_up"] = bos_up
    df["bos_dn"] = bos_dn
    df["choch_up"] = choch_up
    df["choch_dn"] = choch_dn
    df["ms_direction"] = direction
    return df
