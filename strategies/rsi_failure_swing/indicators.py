"""RSI failure-swing indicators (Wilder / Cardwell, causal).

A failure swing is a property of RSI alone -- no price comparison,
which is what separates it from rsi_divergence. Bullish failure
swing (Wilder's bottom pattern): RSI dips below 30, rallies to a
swing high, pulls back to a HIGHER swing low, then breaks above
that intervening swing high. The second low failing to reach the
first low is the "failure": downside momentum is exhausted even
though price may still be falling. Bearish mirrors with 70.

Pivots use a 2-bar lag: a pivot centered at j is only confirmed
at bar j+2 (it must be the extreme over bars j-2..j+2), so a
failure-swing bar never reads unconfirmed data. The trigger is
RSI crossing the intervening swing extreme on a later bar.

Columns:
    rsi          -- Wilder RSI(14)
    rsi_fs_dir   -- +1 on a bullish failure-swing trigger bar,
                    -1 on a bearish trigger bar, else 0
    atr          -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

LAG = 2
RSI_N = 14
OVERSOLD = 30.0
OVERBOUGHT = 70.0


def failure_swing_dir(rsi_v: np.ndarray) -> np.ndarray:
    """Direction array for a raw RSI series (pure, testable).

    Returns +1 on the first bar where RSI breaks above the
    intervening swing high of a completed bullish pattern
    (low < 30, high, higher low), -1 on the mirror, else 0.
    Each pivot triple fires at most once.
    """
    n = len(rsi_v)
    direction = np.zeros(n, dtype=int)
    # pivots in chronological order: (bar, kind, value), kind 'L'/'H'
    pivots: list[tuple[int, str, float]] = []
    fired: set[tuple[int, int, int, str]] = set()
    for i in range(n):
        j = i - LAG
        if 2 <= j < n:
            lo = np.min(rsi_v[j - 2:j + 3]) if np.all(np.isfinite(rsi_v[j - 2:j + 3])) else np.nan
            hi = np.max(rsi_v[j - 2:j + 3]) if np.all(np.isfinite(rsi_v[j - 2:j + 3])) else np.nan
            if np.isfinite(lo) and rsi_v[j] <= lo:
                if pivots and pivots[-1][1] == "L":
                    # keep strict alternation: a later, deeper low
                    # replaces the previous low; a shallower one is
                    # ignored rather than appended
                    if rsi_v[j] < pivots[-1][2]:
                        pivots[-1] = (j, "L", float(rsi_v[j]))
                else:
                    pivots.append((j, "L", float(rsi_v[j])))
            if np.isfinite(hi) and rsi_v[j] >= hi:
                if pivots and pivots[-1][1] == "H":
                    if rsi_v[j] > pivots[-1][2]:
                        pivots[-1] = (j, "H", float(rsi_v[j]))
                else:
                    pivots.append((j, "H", float(rsi_v[j])))
        if len(pivots) >= 3 and np.isfinite(rsi_v[i]):
            p1, p2, p3 = pivots[-3], pivots[-2], pivots[-1]
            if p1[1] == "L" and p2[1] == "H" and p3[1] == "L":
                key = (p1[0], p2[0], p3[0], "bull")
                if p1[2] < OVERSOLD and p3[2] > p1[2] and rsi_v[i] > p2[2] and key not in fired:
                    direction[i] = 1
                    fired.add(key)
            elif p1[1] == "H" and p2[1] == "L" and p3[1] == "H":
                key = (p1[0], p2[0], p3[0], "bear")
                if p1[2] > OVERBOUGHT and p3[2] < p1[2] and rsi_v[i] < p2[2] and key not in fired:
                    direction[i] = -1
                    fired.add(key)
    return direction


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsi = B.rsi(df["c"], RSI_N)
    df["rsi"] = rsi
    df["rsi_fs_dir"] = failure_swing_dir(rsi.to_numpy(dtype=float))
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
