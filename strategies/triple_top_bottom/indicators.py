"""Triple top/bottom indicators (causal, 2-bar pivot lag).

A pivot centered at bar j is only usable on bars >= j+2: at bar
i we confirm the pivot at j = i-2 by checking it is the extreme
of bars j-2..j+2, all of which are known by bar i's close. No
signal ever reads a bar after its own close.

Columns:
    triple_dir -- +1 on a confirmed triple-bottom bar (long),
                  -1 on a confirmed triple-top bar (short), else 0
    atr        -- Wilder ATR(14) for the risk layer

Triple top: three pivot highs within 1.5% of each other, pairwise
separated by >= 5 bars, first-to-last span <= 60 bars, confirmed
by a close below the lowest intervening pivot low. Triple bottom
is the mirror.
"""

import numpy as np
import pandas as pd

from strategies import base as B

LAG = 2
TOL = 0.015
MIN_SEP = 5
WINDOW = 60


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)

    highs: list[tuple[int, float]] = []  # (bar, price) pivot highs
    lows: list[tuple[int, float]] = []  # (bar, price) pivot lows
    fired: set[tuple[int, int, str]] = set()
    direction = np.zeros(n, dtype=int)

    for i in range(n):
        j = i - LAG
        if 2 <= j < n:
            # pivot high at j: extreme of the 5-bar window around j
            if h[j] >= np.max(h[j - 2:j + 3]):
                if highs and j - highs[-1][0] <= LAG:
                    if h[j] > highs[-1][1]:
                        highs[-1] = (j, float(h[j]))
                else:
                    highs.append((j, float(h[j])))
            if l[j] <= np.min(l[j - 2:j + 3]):
                if lows and j - lows[-1][0] <= LAG:
                    if l[j] < lows[-1][1]:
                        lows[-1] = (j, float(l[j]))
                else:
                    lows.append((j, float(l[j])))

        # triple top: last three pivot highs
        if len(highs) >= 3:
            t3 = highs[-3:]
            vals = [v for _, v in t3]
            if (
                t3[-1][0] - t3[0][0] <= WINDOW
                and t3[1][0] - t3[0][0] >= MIN_SEP
                and t3[2][0] - t3[1][0] >= MIN_SEP
                and (max(vals) - min(vals)) / (sum(vals) / 3.0) <= TOL
            ):
                between = [v for idx, v in lows if t3[0][0] < idx < t3[-1][0]]
                key = (t3[0][0], t3[-1][0], "top")
                if between and c[i] < min(between) and key not in fired:
                    direction[i] = -1
                    fired.add(key)

        # triple bottom: last three pivot lows
        if len(lows) >= 3:
            b3 = lows[-3:]
            vals = [v for _, v in b3]
            if (
                b3[-1][0] - b3[0][0] <= WINDOW
                and b3[1][0] - b3[0][0] >= MIN_SEP
                and b3[2][0] - b3[1][0] >= MIN_SEP
                and (max(vals) - min(vals)) / (sum(vals) / 3.0) <= TOL
            ):
                between = [v for idx, v in highs if b3[0][0] < idx < b3[-1][0]]
                key = (b3[0][0], b3[-1][0], "bottom")
                if between and c[i] > max(between) and key not in fired:
                    direction[i] = 1
                    fired.add(key)

    df["triple_dir"] = direction
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
