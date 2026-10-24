"""ABCD harmonic pattern on 5-bar zigzag pivots (causal, no lookahead).

Pipeline, computed bar by bar using only data through bar i:

1. Zigzag pivots: bar j is a swing high when its high is the maximum
   over [j-5, j+5], a swing low when its low is the minimum over the
   same window. A pivot at j is therefore CONFIRMED at bar j+5 — the
   per-bar scan below only ever sees pivots with index <= i-5, so no
   future bar can change an emitted signal. Consecutive same-type
   pivots resolve to the most extreme one (a later confirmed pivot
   replaces an earlier same-type one only if more extreme, and only
   among pivots confirmed so far — history already emitted is never
   rewritten).

2. Pattern test on the last four confirmed pivots (A, B, C, D):

   Bullish (A high, B low, C lower high, D low) -> long at D:
       A > B, C > B, C < A, D < B
       AB = A - B, BC = C - B, CD = C - D
   Bearish (A low, B high, C higher low, D high) -> short at D:
       B > A, C < B, C > A, D > B
       AB = B - A, BC = B - C, CD = D - C
   Both require:
       BC in [38.2%, 88.6%] of AB
       CD in [127.2%, 161.8%] of BC
       |CD| within 20% of |AB|  (0.8 <= CD/AB <= 1.2)

   A pattern fires exactly once, on the bar its D pivot confirms
   (bar D+5); the pivot set must change before another can fire.

Columns:

    abcd_dir    -- +1 on a bullish completion bar, -1 bearish, else 0
    abcd_d_price -- D pivot price on a completion bar, NaN otherwise
    abcd_cd     -- CD leg size on a completion bar, NaN otherwise
    atr         -- Wilder ATR(14) for the risk layer

No lookahead: pivot confirmation, alternation, and the pattern test
all read bars <= i.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CONFIRM = 5            # bars each side to confirm a zigzag pivot
BC_AB_LO, BC_AB_HI = 0.382, 0.886   # BC retracement band of AB
CD_BC_LO, CD_BC_HI = 1.272, 1.618   # CD extension band of BC
CD_AB_LO, CD_AB_HI = 0.8, 1.2       # |CD| within 20% of |AB|


def classify_abcd(four):
    """four = [(idx, price, kind)] oldest-first, kind=+1 high / -1 low.

    Returns ("bull"/"bear", cd_size, d_price) or None.
    """
    kinds = [p[2] for p in four]
    A, Bp, C, D = (p[1] for p in four)
    if kinds == [1, -1, 1, -1]:
        if not (A > Bp and C > Bp and C < A and D < Bp):
            return None
        AB, BC, CD = A - Bp, C - Bp, C - D
    elif kinds == [-1, 1, -1, 1]:
        if not (Bp > A and C < Bp and C > A and D > Bp):
            return None
        AB, BC, CD = Bp - A, Bp - C, D - C
    else:
        return None
    if min(AB, BC, CD) <= 0:
        return None
    if not (BC_AB_LO <= BC / AB <= BC_AB_HI):
        return None
    if not (CD_BC_LO <= CD / BC <= CD_BC_HI):
        return None
    if not (CD_AB_LO <= CD / AB <= CD_AB_HI):
        return None
    return ("bull" if kinds[0] == 1 else "bear", CD, D)


def add_indicators(df: pd.DataFrame, confirm: int = CONFIRM) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)

    confirmed = []  # list of (idx, price, kind), strictly causal
    abcd_dir = np.zeros(n, dtype=int)
    d_price = np.full(n, np.nan)
    cd_size = np.full(n, np.nan)
    last_fired_d = -1
    for i in range(n):
        j = i - confirm
        if j >= confirm:
            # Window [j-confirm, j+confirm] is fully known at bar i.
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
        if len(confirmed) >= 4:
            four = confirmed[-4:]
            if four[-1][0] != last_fired_d:
                res = classify_abcd(four)
                if res is not None:
                    direction, cd, dpx = res
                    last_fired_d = four[-1][0]
                    abcd_dir[i] = 1 if direction == "bull" else -1
                    d_price[i] = dpx
                    cd_size[i] = cd

    df["abcd_dir"] = abcd_dir
    df["abcd_d_price"] = d_price
    df["abcd_cd"] = cd_size
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
