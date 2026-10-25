"""Double top / double bottom on 5-bar zigzag pivots (causal).

A double top is two swing highs within 1.5% of each other separated by
a swing low (the neckline); a double bottom is the mirror. The pattern
is only "pending" once the second extreme confirms (5-bar lag, same
causal zigzag as abcd_pattern), and it stays pending until price
invalidates it by exceeding the second extreme. The trade itself is
the neckline break, handled in signals.py.

Columns:
    dtb_dir     -- -1 while a double top is pending, +1 double bottom, else 0
    dtb_neck    -- neckline price while pending, NaN otherwise
    dtb_extreme -- second extreme price (invalidation level), NaN otherwise
    atr         -- Wilder ATR(14) for the risk layer

No lookahead: pivots confirm 5 bars after they form, and pending state
only ever reads confirmed pivots and closes through bar i.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CONFIRM = 5
TOL = 0.015  # the two extremes must agree within 1.5%


def add_indicators(df: pd.DataFrame, confirm: int = CONFIRM) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)

    confirmed: list[tuple[int, float, int]] = []  # (idx, price, kind)
    pending_dir = 0
    pending_neck = float("nan")
    pending_extreme = float("nan")

    dir_col = np.zeros(n, dtype=int)
    neck_col = np.full(n, np.nan)
    ext_col = np.full(n, np.nan)

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

        if pending_dir == 0 and len(confirmed) >= 3:
            k1, k2, k3 = (p[2] for p in confirmed[-3:])
            p1, p2, p3 = confirmed[-3:]
            if (k1, k2, k3) == (1, -1, 1) and abs(p3[1] - p1[1]) / p1[1] <= TOL:
                pending_dir = -1
                pending_neck = p2[1]
                pending_extreme = p3[1]
            elif (k1, k2, k3) == (-1, 1, -1) and abs(p3[1] - p1[1]) / p1[1] <= TOL:
                pending_dir = 1
                pending_neck = p2[1]
                pending_extreme = p3[1]
        elif pending_dir == -1 and c[i] > pending_extreme:
            pending_dir = 0
            pending_neck = float("nan")
            pending_extreme = float("nan")
        elif pending_dir == 1 and c[i] < pending_extreme:
            pending_dir = 0
            pending_neck = float("nan")
            pending_extreme = float("nan")

        dir_col[i] = pending_dir
        neck_col[i] = pending_neck
        ext_col[i] = pending_extreme

    df["dtb_dir"] = dir_col
    df["dtb_neck"] = neck_col
    df["dtb_extreme"] = ext_col
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
