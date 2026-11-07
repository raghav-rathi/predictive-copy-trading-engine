"""Andrews Pitchfork indicators: median-line system (Dr. Alan Andrews).

Pivots are 5-bar local extrema (middle bar extreme vs 2 bars each side),
alternating types, minimum swing 0.9x ATR(14) between consecutive pivots,
usable only 2 bars after the extreme bar (no lookahead).

Fork: the most recent alternating pivot triple P0 (low), P1 (high),
P2 (low) with P2 > P0 defines the bullish fork; the median line runs
from P0 through the midpoint of P1-P2 and is extended forward; the
lower parallel runs through P2 and the upper parallel through P1, both
parallel to the median line. The bearish fork is the mirror image
(P0 high, P1 low, P2 high with P2 < P0; upper parallel through P2,
lower parallel through P1). The fork is recomputed whenever a newer
completed pivot triple forms. Line values are computed in bar-index
space, so all three lines share one slope per fork.
"""

import numpy as np
import pandas as pd

from strategies import base as B

INDICATOR_COLS = [
    "atr14",
    "pf_bullish",
    "pf_bearish",
    "pf_bull_median",
    "pf_bull_lower",
    "pf_bull_upper",
    "pf_bear_median",
    "pf_bear_lower",
    "pf_bear_upper",
]

MIN_SWING_ATR = 0.9


def _fractal_pivots(h, l, atr_v):
    """Return list of pivots: dicts with idx, confirm, price, kind."""
    n = len(h)
    cands = []
    for j in range(2, n - 2):
        if h[j] >= h[j - 2:j + 3].max() and h[j] > h[j - 1] and h[j] > h[j + 1]:
            cands.append({"idx": j, "confirm": j + 2, "price": float(h[j]), "kind": "H"})
        elif l[j] <= l[j - 2:j + 3].min() and l[j] < l[j - 1] and l[j] < l[j + 1]:
            cands.append({"idx": j, "confirm": j + 2, "price": float(l[j]), "kind": "L"})
    pivots = []
    for cd in cands:
        if not pivots:
            pivots.append(cd)
            continue
        last = pivots[-1]
        a = atr_v[cd["idx"]] if np.isfinite(atr_v[cd["idx"]]) else 0.0
        if cd["kind"] == last["kind"]:
            if (cd["kind"] == "H" and cd["price"] > last["price"]) or (
                cd["kind"] == "L" and cd["price"] < last["price"]
            ):
                pivots[-1] = cd
            continue
        if abs(cd["price"] - last["price"]) >= MIN_SWING_ATR * a:
            pivots.append(cd)
    return pivots


def _fork_triples(pivots):
    """Return (bullish, bearish) lists of fork triples.

    Each triple: dict with p0, p1, p2 pivots and completion bar.
    """
    bull, bear = [], []
    for k in range(len(pivots) - 2):
        w = pivots[k:k + 3]
        kinds = [p["kind"] for p in w]
        if kinds == ["L", "H", "L"] and w[2]["price"] > w[0]["price"]:
            bull.append({"p0": w[0], "p1": w[1], "p2": w[2],
                         "completion": w[2]["confirm"]})
        elif kinds == ["H", "L", "H"] and w[2]["price"] < w[0]["price"]:
            bear.append({"p0": w[0], "p1": w[1], "p2": w[2],
                         "completion": w[2]["confirm"]})
    return bull, bear


def _fork_lines(triple, n):
    """Per-bar (median, lower, upper) line values for one fork triple.

    Returns three float arrays of length n (NaN before completion).
    """
    p0, p1, p2 = triple["p0"], triple["p1"], triple["p2"]
    mid_idx = 0.5 * (p1["idx"] + p2["idx"])
    mid_price = 0.5 * (p1["price"] + p2["price"])
    slope = (mid_price - p0["price"]) / (mid_idx - p0["idx"])
    start = triple["completion"]
    idx = np.arange(n, dtype=float)
    median = p0["price"] + slope * (idx - p0["idx"])
    if p0["kind"] == "L":
        # Bullish fork: upper through P1 (high), lower through P2 (low).
        upper = p1["price"] + slope * (idx - p1["idx"])
        lower = p2["price"] + slope * (idx - p2["idx"])
    else:
        # Bearish fork: upper through P2 (high), lower through P1 (low).
        upper = p2["price"] + slope * (idx - p2["idx"])
        lower = p1["price"] + slope * (idx - p1["idx"])
    median[:start] = np.nan
    upper[:start] = np.nan
    lower[:start] = np.nan
    return median, lower, upper


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    atr_v = df["atr14"].to_numpy()
    pivots = _fractal_pivots(df["h"].to_numpy(), df["l"].to_numpy(), atr_v)
    bull_triples, bear_triples = _fork_triples(pivots)
    bullish = np.zeros(n)
    bearish = np.zeros(n)
    bull_med = np.full(n, np.nan)
    bull_low = np.full(n, np.nan)
    bull_up = np.full(n, np.nan)
    bear_med = np.full(n, np.nan)
    bear_low = np.full(n, np.nan)
    bear_up = np.full(n, np.nan)
    # Sweep bars once; each direction uses its latest completed triple.
    for triples, flag, med_c, low_c, up_c in (
        (bull_triples, bullish, bull_med, bull_low, bull_up),
        (bear_triples, bearish, bear_med, bear_low, bear_up),
    ):
        ti = 0
        cur = None
        cur_lines = None
        for i in range(n):
            while ti < len(triples) and triples[ti]["completion"] <= i:
                cur = triples[ti]
                cur_lines = _fork_lines(cur, n)
                ti += 1
            if cur is not None:
                flag[i] = 1.0
                med_c[i] = cur_lines[0][i]
                low_c[i] = cur_lines[1][i]
                up_c[i] = cur_lines[2][i]
    df["pf_bullish"] = bullish
    df["pf_bearish"] = bearish
    df["pf_bull_median"] = bull_med
    df["pf_bull_lower"] = bull_low
    df["pf_bull_upper"] = bull_up
    df["pf_bear_median"] = bear_med
    df["pf_bear_lower"] = bear_low
    df["pf_bear_upper"] = bear_up
    return df
