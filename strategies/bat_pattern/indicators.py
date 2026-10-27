"""Scott Carney Bat pattern (2001), causal zigzag engine.

Pipeline (same causality contract as harmonic_gartley):
  1. Zigzag pivots: a bar is a swing high (low) when its high (low)
     is the extreme over [i-5, i+5]. Consecutive same-type extremes
     resolve to the most extreme, so pivots strictly alternate.
  2. Per-bar scan: at bar i only pivots confirmed through bar i
     (index <= i-5) are visible. The last 5 confirmed pivots are
     tested as XABCD. Bullish (X low, A high, B low, C high, D low):
     AB/XA in [0.382, 0.500], BC/AB in [0.382, 0.886],
     CD/BC in [1.618, 2.618], AD/XA = 0.886 (+-6%), D > X.
     Bearish is the mirror. The Bat completes deeper than the
     Gartley (0.886 vs 0.786) and its CD leg is an extension, not
     a retracement — that is the whole difference between the two
     patterns in this library.
  3. Completion fires once, on the bar the D pivot confirms (D + 5).
     One signal per pattern: the pivot set must change first.

The backtest harness cannot express the classical PRZ stop beyond
X, so risk.py uses a 2xATR hard stop as the executable proxy.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CONFIRM = 5
TOL = 0.06
AB_XA_LO, AB_XA_HI = 0.382, 0.500
BC_AB_LO, BC_AB_HI = 0.382, 0.886
CD_BC_LO, CD_BC_HI = 1.618, 2.618
AD_XA = 0.886


def _within(x: float, target: float, tol: float = TOL) -> bool:
    return abs(x - target) <= tol * target


def _classify(five, tol: float = TOL):
    kinds = [p[2] for p in five]
    X, A, B, C, D = (p[1] for p in five)
    if kinds == [-1, 1, -1, 1, -1]:
        if not (A > X and B < A and C > B and D < C and D > X):
            return None
        XA, AB, BC, CD, AD = A - X, A - B, C - B, C - D, A - D
        if min(XA, AB, BC, CD, AD) <= 0:
            return None
        if not (AB_XA_LO <= AB / XA <= AB_XA_HI):
            return None
        if not (BC_AB_LO <= BC / AB <= BC_AB_HI):
            return None
        if not (CD_BC_LO <= CD / BC <= CD_BC_HI):
            return None
        if not _within(AD / XA, AD_XA, tol):
            return None
        return "bull"
    if kinds == [1, -1, 1, -1, 1]:
        if not (A < X and B > A and C < B and D > C and D < X):
            return None
        XA, AB, BC, CD, AD = X - A, B - A, B - C, D - C, D - A
        if min(XA, AB, BC, CD, AD) <= 0:
            return None
        if not (AB_XA_LO <= AB / XA <= AB_XA_HI):
            return None
        if not (BC_AB_LO <= BC / AB <= BC_AB_HI):
            return None
        if not (CD_BC_LO <= CD / BC <= CD_BC_HI):
            return None
        if not _within(AD / XA, AD_XA, tol):
            return None
        return "bear"
    return None


def zigzag_pivots(df: pd.DataFrame, confirm: int = CONFIRM):
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    n = len(df)
    raw = []
    for j in range(confirm, n - confirm):
        if h[j] >= h[j - confirm : j + confirm + 1].max():
            raw.append((j, h[j], 1))
        if l[j] <= l[j - confirm : j + confirm + 1].min():
            raw.append((j, l[j], -1))
    raw.sort(key=lambda p: p[0])
    out = []
    for j, px, kind in raw:
        if not out or kind != out[-1][2]:
            out.append((j, px, kind))
        else:
            pj, ppx, _ = out[-1]
            if (kind == 1 and px > ppx) or (kind == -1 and px < ppx):
                out[-1] = (j, px, kind)
    return out


def add_indicators(df: pd.DataFrame, confirm: int = CONFIRM, tol: float = TOL) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    pivots = zigzag_pivots(df, confirm)
    prz = np.zeros(n, dtype=int)
    bdir = np.zeros(n, dtype=int)
    last_fired_d = -1
    k = 0
    for i in range(n):
        while k < len(pivots) and pivots[k][0] <= i - confirm:
            k += 1
        if k >= 5:
            five = pivots[k - 5 : k]
            if five[-1][0] != last_fired_d:
                res = _classify(five, tol)
                if res is not None:
                    last_fired_d = five[-1][0]
                    prz[i] = 1
                    bdir[i] = 1 if res == "bull" else -1
    df["prz"] = prz
    df["bat_dir"] = bdir
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
