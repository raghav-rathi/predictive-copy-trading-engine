"""Andrews Pitchfork signals.

Long: the low comes within 0.25x ATR(14) of the bullish fork's lower
parallel and the bar closes back above it (bounce). Target is the
median line — exit long at a close reaching the median line. Also exit
on a close outside the fork, beyond the opposite (upper) parallel.
Short is the mirror image off the bearish fork's upper parallel,
targeting the median line. A bounce counts once: consecutive bars
meeting the same bounce condition do not re-fire.
"""

import numpy as np
import pandas as pd

TOUCH_ATR = 0.25


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    o = df["o"].to_numpy()
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    c = df["c"].to_numpy()
    atr = df["atr14"].to_numpy()
    bull = df["pf_bullish"].to_numpy()
    bear = df["pf_bearish"].to_numpy()
    bull_med = df["pf_bull_median"].to_numpy()
    bull_low = df["pf_bull_lower"].to_numpy()
    bull_up = df["pf_bull_upper"].to_numpy()
    bear_med = df["pf_bear_median"].to_numpy()
    bear_low = df["pf_bear_lower"].to_numpy()
    bear_up = df["pf_bear_upper"].to_numpy()
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    prev_bull_bounce = False
    prev_bear_bounce = False
    for i in range(n):
        a = atr[i] if np.isfinite(atr[i]) else 0.0
        bull_bounce = False
        if bull[i] == 1.0 and np.isfinite(bull_low[i]):
            if (
                l[i] >= bull_low[i] - TOUCH_ATR * a
                and l[i] <= bull_low[i] + TOUCH_ATR * a
                and c[i] > bull_low[i]
            ):
                bull_bounce = True
        bear_bounce = False
        if bear[i] == 1.0 and np.isfinite(bear_up[i]):
            if (
                h[i] <= bear_up[i] + TOUCH_ATR * a
                and h[i] >= bear_up[i] - TOUCH_ATR * a
                and c[i] < bear_up[i]
            ):
                bear_bounce = True
        if bull_bounce and not prev_bull_bounce:
            long_entry[i] = True
        if bear_bounce and not prev_bear_bounce:
            short_entry[i] = True
        prev_bull_bounce = bull_bounce
        prev_bear_bounce = bear_bounce
        if bull[i] == 1.0:
            if np.isfinite(bull_med[i]) and c[i] >= bull_med[i]:
                long_exit[i] = True
            elif np.isfinite(bull_up[i]) and c[i] > bull_up[i]:
                long_exit[i] = True
        if bear[i] == 1.0:
            if np.isfinite(bear_med[i]) and c[i] <= bear_med[i]:
                short_exit[i] = True
            elif np.isfinite(bear_low[i]) and c[i] < bear_low[i]:
                short_exit[i] = True
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
