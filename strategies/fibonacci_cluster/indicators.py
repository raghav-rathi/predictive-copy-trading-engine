"""Fibonacci cluster (confluence zone) construction.

ZigZag swings from 5-bar fractal pivots, then Fibonacci retracement
levels of the last 3 completed swings, then clusters where levels
from different swings coincide.

    pivot      -- 5-bar fractal: high pivot if h[i] is the max of
                  h[i-2..i+2], low pivot if l[i] is the min of
                  l[i-2..i+2]. A pivot centred on bar i is only
                  *confirmed* at bar i+2, so the series is shifted
                  +2 bars -- no lookahead.
    swing      -- consecutive confirmed pivots, zigzag-filtered:
                  pivots must alternate high/low, a new pivot must
                  move >= MIN_SWING_PCT (2%) from the last pivot,
                  and a same-type pivot replaces the last only if
                  more extreme (higher high / lower low).
    levels     -- for each of the last 3 completed swings, the
                  38.2% / 50% / 61.8% retracements. Up swing
                  (low -> high): level = high - r * (high - low).
                  Down swing (high -> low): level = low + r * (high - low).
    cluster    -- levels from >= 2 different swings whose prices
                  fall within CLUSTER_WIDTH_ATR (0.5x ATR(14)) of
                  each other; cluster price = mean of member levels.

Columns:

    atr            -- Wilder ATR(14) for the risk layer and widths
    fib_sup        -- nearest support cluster price (< close), NaN if none
    fib_sup_n      -- member count of that cluster
    fib_res        -- nearest resistance cluster price (> close), NaN if none
    fib_res_n      -- member count of that cluster
    fib_n_clusters -- number of clusters (support + resistance) this bar
    fib_n_pivots   -- confirmed zigzag pivots so far
    fib_n_swings   -- completed swings so far

No lookahead: pivots enter only after their 2-bar confirmation, and
levels/clusters on bar j use confirmed pivots through bar j only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_N = 14
PIVOT_N = 5          # 5-bar fractal (2 bars each side)
MIN_SWING_PCT = 0.02  # minimum swing move between consecutive pivots
LEVELS = (0.382, 0.5, 0.618)
CLUSTER_WIDTH_ATR = 0.5  # cluster width in ATR multiples
WARMUP = 120


def fractal_pivots(h: np.ndarray, l: np.ndarray):
    """Return list of (confirm_bar, type, price) for 5-bar fractal pivots.

    type +1 = high pivot, -1 = low pivot. A pivot centred on bar i is
    confirmed at bar i+2 (the two bars to its right must print first).
    """
    n = len(h)
    out = []
    for i in range(2, n - 2):
        if h[i] == h[i - 2:i + 3].max() and h[i] >= h[i - 1]:
            out.append((i + 2, 1, float(h[i])))
        if l[i] == l[i - 2:i + 3].min() and l[i] <= l[i - 1]:
            out.append((i + 2, -1, float(l[i])))
    out.sort(key=lambda p: p[0])
    return out


def cluster_levels(levels, width):
    """Group (price, swing_id) levels into clusters.

    Adjacent sorted levels within ``width`` of each other form one
    group; a group is a cluster when it holds >= 2 levels from
    different swings. Returns list of (cluster_price, member_count).
    """
    if not levels:
        return []
    levels = sorted(levels, key=lambda x: x[0])
    groups = [[levels[0]]]
    for lv in levels[1:]:
        if lv[0] - groups[-1][-1][0] <= width:
            groups[-1].append(lv)
        else:
            groups.append([lv])
    clusters = []
    for g in groups:
        swing_ids = {s for _, s in g}
        if len(swing_ids) >= 2:
            price = float(np.mean([p for p, _ in g]))
            clusters.append((price, len(g)))
    return clusters


def add_indicators(df: pd.DataFrame,
                   cluster_width_atr: float = CLUSTER_WIDTH_ATR) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    atr_s = B.atr(df["h"], df["l"], df["c"], ATR_N).to_numpy(dtype=float)

    pivots = fractal_pivots(h, l)
    by_bar: dict[int, list] = {}
    for bar, typ, price in pivots:
        by_bar.setdefault(bar, []).append((typ, price))

    fib_sup = np.full(n, np.nan)
    fib_sup_n = np.zeros(n, dtype=int)
    fib_res = np.full(n, np.nan)
    fib_res_n = np.zeros(n, dtype=int)
    n_clusters = np.zeros(n, dtype=int)
    n_pivots = np.zeros(n, dtype=int)
    n_swings = np.zeros(n, dtype=int)

    # zigzag pivot list: each entry (type, price); alternates by construction
    zz: list[tuple[int, float]] = []

    for j in range(n):
        for typ, price in by_bar.get(j, ()):  # confirmed pivots arriving now
            if not zz:
                zz.append((typ, price))
            elif zz[-1][0] == typ:
                # same type: keep only the more extreme pivot
                if (typ == 1 and price > zz[-1][1]) or (typ == -1 and price < zz[-1][1]):
                    zz[-1] = (typ, price)
            else:
                # opposite type: needs a >= 2% swing from the last pivot
                if abs(price - zz[-1][1]) / zz[-1][1] >= MIN_SWING_PCT:
                    zz.append((typ, price))
        n_pivots[j] = len(zz)
        n_swings[j] = max(0, len(zz) - 1)

        if len(zz) >= 4 and np.isfinite(atr_s[j]):
            # last 3 completed swings = last 3 consecutive pivot pairs
            swings = list(zip(zz[-4:-1], zz[-3:]))
            levels = []
            for sid, ((t0, p0), (t1, p1)) in enumerate(swings):
                lo, hi = min(p0, p1), max(p0, p1)
                for r in LEVELS:
                    # retracement measured from the swing's far end back
                    # toward its start: same formula either direction
                    if t0 == -1:  # up swing low -> high: levels below the high
                        levels.append((hi - r * (hi - lo), sid))
                    else:          # down swing high -> low: levels above the low
                        levels.append((lo + r * (hi - lo), sid))
            width = cluster_width_atr * atr_s[j]
            clusters = cluster_levels(levels, width)
            n_clusters[j] = len(clusters)
            sup = [(p, m) for p, m in clusters if p < c[j]]
            res = [(p, m) for p, m in clusters if p > c[j]]
            if sup:
                fib_sup[j], fib_sup_n[j] = max(sup, key=lambda x: x[0])
            if res:
                fib_res[j], fib_res_n[j] = min(res, key=lambda x: x[0])

    df["atr"] = atr_s
    df["fib_sup"] = fib_sup
    df["fib_sup_n"] = fib_sup_n
    df["fib_res"] = fib_res
    df["fib_res_n"] = fib_res_n
    df["fib_n_clusters"] = n_clusters
    df["fib_n_pivots"] = n_pivots
    df["fib_n_swings"] = n_swings
    return df
