"""Scott Carney Cypher harmonic pattern on lagged 5-bar pivots.

Geometry (bullish Cypher — X low, A high, B low, C high, D low):
    XA = A - X            (initial up leg)
    AB = A - B            (retracement of XA)
    BC = C - B            (extension past A)
    XC = C - X
    CD = C - D            (deep retracement of XC)
    AB / XA in [38.2%, 61.8%]  (+/- 8 pp tolerance -> [30.2%, 69.8%])
    BC / AB in [113%, 141.4%]  (+/- 8 pp tolerance -> [105%, 149.4%])
    CD / XC = 78.6%            (+/- 8 pp tolerance -> [70.6%, 86.6%])
    plus structure: A > X, X < B < A, C > A, X < D < B.

Bearish Cypher is the exact mirror (X high, A low, B high, C low,
D high, same ratio bands on the mirrored legs).

Pivot detection is causal, following the ABCD precedent: bar j is
a swing high when its high is the maximum over [j-5, j+5], a swing
low when its low is the minimum over the same window. A pivot at j
is therefore only usable from bar j+5 onward — the scan below only
ever sees pivots with index <= i-5, so no future bar can change an
emitted signal. The five pivots must span at most 60 bars
(D_idx - X_idx <= 60). A pattern fires exactly once, on the bar
its D pivot confirms (bar D+5); the pivot set must change before
another can fire.

Columns:
    cypher_dir    -- +1 on a bullish completion bar, -1 bearish, else 0
    cypher_d_price -- D pivot price on a completion bar, NaN otherwise
    atr           -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

CONFIRM = 5            # bars each side to confirm a pivot
MAX_SPAN = 60          # X..D pivot span cap, in bars
AB_XA_LO, AB_XA_HI = 0.302, 0.698    # 38.2-61.8% +/- 8pp
BC_AB_LO, BC_AB_HI = 1.05, 1.494     # 113-141.4% +/- 8pp
CD_XC_LO, CD_XC_HI = 0.706, 0.866    # 78.6% +/- 8pp


def classify_cypher(five):
    """five = [(idx, price, kind)] oldest-first, kind=+1 high / -1 low.

    Returns ("bull"/"bear", d_price) or None.
    """
    if len(five) != 5:
        return None
    if five[-1][0] - five[0][0] > MAX_SPAN:
        return None
    kinds = [p[2] for p in five]
    X, A, Bp, C, D = (p[1] for p in five)
    if kinds == [-1, 1, -1, 1, -1]:
        # Bullish: X low, A high, B low, C high, D low.
        if not (A > X and X < Bp < A and C > A and X < D < Bp):
            return None
        XA, AB, BC, XC, CD = A - X, A - Bp, C - Bp, C - X, C - D
        direction = "bull"
    elif kinds == [1, -1, 1, -1, 1]:
        # Bearish mirror: X high, A low, B high, C low, D high.
        if not (A < X and X > Bp > A and C < A and X > D > Bp):
            return None
        XA, AB, BC, XC, CD = X - A, Bp - A, Bp - C, X - C, D - C
        direction = "bear"
    else:
        return None
    if min(XA, AB, BC, XC, CD) <= 0:
        return None
    if not (AB_XA_LO <= AB / XA <= AB_XA_HI):
        return None
    if not (BC_AB_LO <= BC / AB <= BC_AB_HI):
        return None
    if not (CD_XC_LO <= CD / XC <= CD_XC_HI):
        return None
    return (direction, D)


def add_indicators(df: pd.DataFrame, confirm: int = CONFIRM) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)

    confirmed = []  # list of (idx, price, kind), strictly causal
    cypher_dir = np.zeros(n, dtype=int)
    d_price = np.full(n, np.nan)
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
        if len(confirmed) >= 5:
            five = confirmed[-5:]
            if five[-1][0] != last_fired_d:
                res = classify_cypher(five)
                if res is not None:
                    direction, dpx = res
                    last_fired_d = five[-1][0]
                    cypher_dir[i] = 1 if direction == "bull" else -1
                    d_price[i] = dpx

    df["cypher_dir"] = cypher_dir
    df["cypher_d_price"] = d_price
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
