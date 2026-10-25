"""Ascending / descending triangle breakout on zigzag pivots.

Ascending triangle: flat resistance (two swing highs within 1%) with
rising support (each swing low higher than the last) — traded long on
a close above resistance. Descending triangle is the mirror: flat
support, falling resistance, traded short on a close below support.
Only the two-sided, confirmed-pivot version is traded here (no
symmetrical triangles: their breakout direction is a coin flip and
the library already has enough two-way noise).

Columns:
    tri_dir   -- +1 ascending pending, -1 descending pending, else 0
    tri_level -- resistance (ascending) or support (descending), else NaN
    atr       -- Wilder ATR(14) for the risk layer

Pending state is sticky: it survives until price breaks out or
invalidates it (ascending: close below the rising support low;
descending: close above the falling resistance high). No lookahead:
same causal 5-bar zigzag confirmation as abcd_pattern.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CONFIRM = 5
FLAT_TOL = 0.01  # the flat side must agree within 1%


def add_indicators(df: pd.DataFrame, confirm: int = CONFIRM) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)

    confirmed: list[tuple[int, float, int]] = []
    pending_dir = 0
    pending_level = float("nan")
    pending_invalid = float("nan")

    dir_col = np.zeros(n, dtype=int)
    level_col = np.full(n, np.nan)

    for i in range(n):
        j = i - confirm
        if j >= confirm:
            if h[j] >= h[j - confirm:j + confirm + 1].max():
                piv = (j, h[j], 1)
                if confirmed and confirmed[-1][2] == 1:
                    if piv[1] > confirmed[-1][1]:
                        confirmed[-1] = piv
                else:
                    confirmed.append(piv)
            if l[j] <= l[j - confirm:j + confirm + 1].min():
                piv = (j, l[j], -1)
                if confirmed and confirmed[-1][2] == -1:
                    if piv[1] < confirmed[-1][1]:
                        confirmed[-1] = piv
                else:
                    confirmed.append(piv)

        if pending_dir == 0:
            highs = [p for p in confirmed if p[2] == 1][-2:]
            lows = [p for p in confirmed if p[2] == -1][-2:]
            if len(highs) == 2 and len(lows) == 2:
                h1, h2 = highs
                l1, l2 = lows
                # both pairs must be among the last 4 confirmed pivots
                recent = confirmed[-4:]
                if h1 in recent and h2 in recent and l1 in recent and l2 in recent:
                    if abs(h2[1] - h1[1]) / h1[1] <= FLAT_TOL and l2[1] > l1[1]:
                        pending_dir = 1
                        pending_level = h2[1]
                        pending_invalid = l2[1]
                    elif abs(l2[1] - l1[1]) / l1[1] <= FLAT_TOL and h2[1] < h1[1]:
                        pending_dir = -1
                        pending_level = l2[1]
                        pending_invalid = h2[1]
        elif pending_dir == 1 and c[i] < pending_invalid:
            pending_dir = 0
            pending_level = float("nan")
            pending_invalid = float("nan")
        elif pending_dir == -1 and c[i] > pending_invalid:
            pending_dir = 0
            pending_level = float("nan")
            pending_invalid = float("nan")

        dir_col[i] = pending_dir
        level_col[i] = pending_level

    df["tri_dir"] = dir_col
    df["tri_level"] = level_col
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
