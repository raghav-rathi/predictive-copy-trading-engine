"""Harmonic Gartley XABCD pattern indicators.

Pipeline (causal, no lookahead):
  1. Zigzag pivots: a bar is a swing high (low) when its high (low) is the
     extreme over [i-5, i+5]. Consecutive same-type extremes are resolved to
     the most extreme, so the pivot list strictly alternates high/low.
  2. Per-bar scan: at bar i only pivots confirmed through bar i (index
     <= i-5) are visible. The last 5 confirmed pivots are tested as XABCD:
       bullish (X low, A high, B low, C high, D low):
         A > X, B < A, C > B, D < C, D > X (D must not exceed X)
         AB = 0.618*XA (+-6%), BC in [0.382, 0.886]*AB,
         CD in [1.272, 1.618]*BC, AD = 0.786*XA (+-6%)
       bearish is the mirror image.
  3. When a pattern first completes (its D pivot confirms, i.e. 5 bars
     after D prints), the completion bar gets prz=1 and gartley_dir=+1/-1.
     One signal per pattern: the pivot set must change before another fires.

Note: the classical PRZ stop sits beyond X; the backtest harness cannot
express that, so risk.py uses a 2xATR hard stop as the executable proxy
(see BACKTEST.md).
"""

import numpy as np
import pandas as pd

from strategies import base as B

CONFIRM = 5          # bars each side to confirm a zigzag pivot
TOL = 0.06           # +-6% on the AB/XA and AD/XA point ratios
AB_XA = 0.618
BC_AB_LO, BC_AB_HI = 0.382, 0.886
CD_BC_LO, CD_BC_HI = 1.272, 1.618
AD_XA = 0.786


def _within(x: float, target: float, tol: float = TOL) -> bool:
    return abs(x - target) <= tol * target


def _classify(five, tol: float = TOL) -> str | None:
    """five = [(idx, price, kind)] oldest-first, kind=+1 high / -1 low."""
    kinds = [p[2] for p in five]
    X, A, B, C, D = (p[1] for p in five)
    if kinds == [-1, 1, -1, 1, -1]:
        # bullish Gartley: X low -> A high -> B low -> C high -> D low
        if not (A > X and B < A and C > B and D < C and D > X):
            return None
        XA, AB, BC, CD, AD = A - X, A - B, C - B, C - D, A - D
        if min(XA, AB, BC, CD, AD) <= 0:
            return None
        if not _within(AB / XA, AB_XA, tol):
            return None
        if not (BC_AB_LO <= BC / AB <= BC_AB_HI):
            return None
        if not (CD_BC_LO <= CD / BC <= CD_BC_HI):
            return None
        if not _within(AD / XA, AD_XA, tol):
            return None
        return "bull"
    if kinds == [1, -1, 1, -1, 1]:
        # bearish Gartley: X high -> A low -> B high -> C low -> D high
        if not (A < X and B > A and C < B and D > C and D < X):
            return None
        XA, AB, BC, CD, AD = X - A, B - A, B - C, D - C, D - A
        if min(XA, AB, BC, CD, AD) <= 0:
            return None
        if not _within(AB / XA, AB_XA, tol):
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
    """All zigzag pivots on the frame: list of (idx, price, kind)."""
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
    # enforce alternation: keep the most extreme of consecutive same-type
    out = []
    for j, px, kind in raw:
        if not out or kind != out[-1][2]:
            out.append((j, px, kind))
        else:
            pj, ppx, _ = out[-1]
            if (kind == 1 and px > ppx) or (kind == -1 and px < ppx):
                out[-1] = (j, px, kind)
    return out


def add_indicators(
    df: pd.DataFrame,
    confirm: int = CONFIRM,
    tol: float = TOL,
) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    pivots = zigzag_pivots(df, confirm)
    prz = np.zeros(n, dtype=int)
    gdir = np.zeros(n, dtype=int)
    last_fired_d = -1
    k = 0  # count of pivots confirmed through the current bar
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
                    gdir[i] = 1 if res == "bull" else -1
    df["prz"] = prz
    df["gartley_dir"] = gdir
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
