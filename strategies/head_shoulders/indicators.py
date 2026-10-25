"""Head and shoulders / inverse head and shoulders on zigzag pivots.

The textbook reversal: three peaks with the middle (head) highest and
the two shoulders lower and roughly equal (within 3%), or the mirror
for the inverse pattern. The neckline connects the two troughs (top
pattern) or the two peaks (inverse); the conservative trigger used
here is the lower trough for tops and the higher peak for bottoms.
The pattern is pending once the right shoulder confirms (5-bar lag)
and stays pending until price exceeds the head (invalidation).

Columns:
    hs_dir     -- -1 while a H&S top is pending, +1 inverse, else 0
    hs_neck    -- neckline price while pending, NaN otherwise
    hs_head    -- head price (invalidation level), NaN otherwise
    atr        -- Wilder ATR(14) for the risk layer

No lookahead: same causal 5-bar zigzag confirmation as abcd_pattern.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CONFIRM = 5
SHOULDER_TOL = 0.03  # shoulders must agree within 3%


def add_indicators(df: pd.DataFrame, confirm: int = CONFIRM) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)

    confirmed: list[tuple[int, float, int]] = []
    pending_dir = 0
    pending_neck = float("nan")
    pending_head = float("nan")

    dir_col = np.zeros(n, dtype=int)
    neck_col = np.full(n, np.nan)
    head_col = np.full(n, np.nan)

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

        if pending_dir == 0 and len(confirmed) >= 5:
            kinds = [p[2] for p in confirmed[-5:]]
            ls, t1, hd, t2, rs = confirmed[-5:]
            if kinds == [1, -1, 1, -1, 1]:
                if hd[1] > ls[1] and hd[1] > rs[1] and abs(rs[1] - ls[1]) / ls[1] <= SHOULDER_TOL:
                    pending_dir = -1
                    pending_neck = min(t1[1], t2[1])
                    pending_head = hd[1]
            elif kinds == [-1, 1, -1, 1, -1]:
                if hd[1] < ls[1] and hd[1] < rs[1] and abs(rs[1] - ls[1]) / ls[1] <= SHOULDER_TOL:
                    pending_dir = 1
                    pending_neck = max(t1[1], t2[1])
                    pending_head = hd[1]
        elif pending_dir == -1 and c[i] > pending_head:
            pending_dir = 0
            pending_neck = float("nan")
            pending_head = float("nan")
        elif pending_dir == 1 and c[i] < pending_head:
            pending_dir = 0
            pending_neck = float("nan")
            pending_head = float("nan")

        dir_col[i] = pending_dir
        neck_col[i] = pending_neck
        head_col[i] = pending_head

    df["hs_dir"] = dir_col
    df["hs_neck"] = neck_col
    df["hs_head"] = head_col
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
