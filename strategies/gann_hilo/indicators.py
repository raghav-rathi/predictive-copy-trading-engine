"""Gann Hi-Lo Activator indicators (Robert Krausz, 1998).

Despite the name, the activator is Krausz's, not Gann's. State is
+1 (bullish) when the close exceeds the previous bar's SMA(3) of
highs, -1 (bearish) when it falls below the previous bar's SMA(3)
of lows, and unchanged otherwise. The plotted line is the SMA of
lows while bullish (support below price) and the SMA of highs
while bearish (resistance above price).

Columns:
    gann_hilo -- the activator line
    hilo_state -- +1 bullish / -1 bearish
    atr        -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 3


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hi = B.sma(df["h"], PERIOD).to_numpy()
    lo = B.sma(df["l"], PERIOD).to_numpy()
    c = df["c"].to_numpy()
    n = len(df)
    hilo = np.full(n, np.nan)
    state = np.zeros(n, dtype=int)
    valid = np.where(~np.isnan(hi) & ~np.isnan(lo))[0]
    if len(valid):
        start = int(valid[0]) + 1
        cur = -1
        state[:start] = -1
        for i in range(start, n):
            if c[i] > hi[i - 1]:
                cur = 1
            elif c[i] < lo[i - 1]:
                cur = -1
            state[i] = cur
            hilo[i] = lo[i] if cur == 1 else hi[i]
    df["gann_hilo"] = hilo
    df["hilo_state"] = state
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
