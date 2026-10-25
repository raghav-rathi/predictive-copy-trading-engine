"""Swing support / resistance bounce on clustered zigzag pivots.

Support and resistance are where price has turned before: swing
highs and lows (5-bar zigzag, causal) from the last 250 bars are
clustered within 0.5% of each other, and a cluster with at least two
touches becomes a level. The trade is the bounce: long when a bar
dips to a support level and closes back above it with an up close,
short on the mirror at resistance. The failure rule is a close beyond
the level by 0.5% (the level broke, not bounced).

Columns:
    sr_support    -- nearest clustered level below the close, else NaN
    sr_resistance -- nearest clustered level above the close, else NaN
    atr           -- Wilder ATR(14) for the risk layer

Levels only change when a new pivot confirms, so they are recomputed
on confirmation bars only — but every value emitted at bar i uses
only pivots confirmed by bar i. No lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CONFIRM = 5
LOOKBACK = 250   # bars of pivot history feeding the levels
CLUSTER_TOL = 0.005  # pivots within 0.5% form one level
MIN_TOUCHES = 2
TOUCH_TOL = 0.003  # bar must dip within 0.3% of the level
FAIL_TOL = 0.005   # close 0.5% beyond the level = failure


def _levels(pivots):
    """Cluster pivot prices; return sorted level prices (>= MIN_TOUCHES)."""
    prices = sorted(p[1] for p in pivots)
    groups = []
    for px in prices:
        if groups and (px - groups[-1][0]) / groups[-1][0] <= CLUSTER_TOL:
            groups[-1].append(px)
        else:
            groups.append([px])
    return [float(np.mean(g)) for g in groups if len(g) >= MIN_TOUCHES]


def add_indicators(df: pd.DataFrame, confirm: int = CONFIRM) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)

    confirmed: list[tuple[int, float, int]] = []
    levels: list[float] = []
    levels_dirty = True

    sup_col = np.full(n, np.nan)
    res_col = np.full(n, np.nan)

    for i in range(n):
        j = i - confirm
        if j >= confirm:
            added = False
            if h[j] >= h[j - confirm:j + confirm + 1].max():
                piv = (j, h[j], 1)
                if confirmed and confirmed[-1][2] == 1:
                    if piv[1] > confirmed[-1][1]:
                        confirmed[-1] = piv
                        added = True
                else:
                    confirmed.append(piv)
                    added = True
            if l[j] <= l[j - confirm:j + confirm + 1].min():
                piv = (j, l[j], -1)
                if confirmed and confirmed[-1][2] == -1:
                    if piv[1] < confirmed[-1][1]:
                        confirmed[-1] = piv
                        added = True
                else:
                    confirmed.append(piv)
                    added = True
            if added:
                levels_dirty = True
        if levels_dirty:
            recent = [p for p in confirmed if i - p[0] <= LOOKBACK]
            levels = _levels(recent)
            levels_dirty = False
        below = [lv for lv in levels if lv < c[i]]
        above = [lv for lv in levels if lv > c[i]]
        sup_col[i] = max(below) if below else np.nan
        res_col[i] = min(above) if above else np.nan

    df["sr_support"] = sup_col
    df["sr_resistance"] = res_col
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
