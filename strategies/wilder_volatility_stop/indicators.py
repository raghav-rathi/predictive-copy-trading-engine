"""Wilder Volatility Stop indicators: ATR(7) + SIC state machine.

Trend is +1 (up) or -1 (down). SIC is the highest close reached while up
(lowest close while down); the stop trails 3xATR(7) behind the SIC. The
state machine is seeded at the first bar at/after index 29 (warmup - 1):
trend +1 if close > SMA(20) else -1, SIC = that bar's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_N = 7
MULT = 3.0
SMA_N = 20
START_IDX = 29

INDICATOR_COLS = ["vol_stop", "vol_trend", "vol_sic", "atr7"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["atr7"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    sma20 = B.sma(df["c"], SMA_N)

    c = df["c"].to_numpy(dtype=float)
    a = df["atr7"].to_numpy(dtype=float)
    s = sma20.to_numpy(dtype=float)
    n = len(df)
    stop = np.full(n, np.nan)
    trend = np.full(n, np.nan)
    sic = np.full(n, np.nan)

    # Seed at the first bar with valid ATR + SMA at/after START_IDX.
    valid = [i for i in range(START_IDX, n) if np.isfinite(a[i]) and np.isfinite(s[i])]
    if valid:
        j = valid[0]
        tr = 1.0 if c[j] > s[j] else -1.0
        sc = c[j]
        st = sc - MULT * a[j] if tr == 1.0 else sc + MULT * a[j]
        trend[j] = tr
        sic[j] = sc
        stop[j] = st
        for i in range(j + 1, n):
            if not np.isfinite(a[i]):
                trend[i] = tr
                sic[i] = sc
                stop[i] = st
                continue
            if tr == 1.0:
                # Close below the PRIOR bar's stop flips the trend; the
                # stop used is the one already fixed at bar i-1.
                if c[i] < stop[i - 1]:
                    tr = -1.0
                    sc = c[i]
                    st = sc + MULT * a[i]
                else:
                    sc = max(sc, c[i])
                    st = sc - MULT * a[i]
            else:
                if c[i] > stop[i - 1]:
                    tr = 1.0
                    sc = c[i]
                    st = sc - MULT * a[i]
                else:
                    sc = min(sc, c[i])
                    st = sc + MULT * a[i]
            trend[i] = tr
            sic[i] = sc
            stop[i] = st

    df["vol_stop"] = stop
    df["vol_trend"] = trend
    df["vol_sic"] = sic
    return df
