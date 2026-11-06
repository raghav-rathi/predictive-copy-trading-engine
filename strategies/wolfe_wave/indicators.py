"""Wolfe Wave indicators: zigzag swing detector + Wolfe Wave geometry.

Zigzag: 5-bar local extrema (a pivot high is the highest high of its
5-bar window, strictly above both neighbours; same for lows), minimum
swing 0.9x ATR(14) between consecutive pivots, alternating pivot types,
and a pivot is only usable 2 bars after its extreme bar (its
confirmation index is extreme index + 2). All pattern geometry is
evaluated from pivots confirmed by the current bar — no lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B

INDICATOR_COLS = [
    "atr14",
    "ww_line13",
    "ww_line24",
    "ww_epa",
    "ww_bullish",
    "ww_bearish",
    "ww_complete",
]

MIN_SWING_ATR = 0.9


def _zigzag_pivots(h, l, atr_v):
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


def _line(p1, p2):
    m = (p2["price"] - p1["price"]) / (p2["idx"] - p1["idx"])
    b = p1["price"] - m * p1["idx"]
    return m, b


def _wolfe_patterns(pivots):
    """Return list of completed Wolfe Wave patterns."""
    pats = []
    for k in range(len(pivots) - 4):
        w = pivots[k:k + 5]
        kinds = [p["kind"] for p in w]
        p1, p2, p3, p4, p5 = w
        m13, b13 = _line(p1, p3)
        m24, b24 = _line(p2, p4)
        if abs(m13 - m24) < 1e-12:
            continue
        x_int = (b24 - b13) / (m13 - m24)
        if not (x_int > p5["idx"] and x_int < p5["idx"] + 300):
            continue
        mepa, bepa = _line(p1, p4)
        if kinds == ["L", "H", "L", "H", "L"]:
            if not (p3["price"] < p1["price"] and p4["price"] < p2["price"]):
                continue
            if not (p5["price"] < m13 * p5["idx"] + b13):
                continue
            if not (m13 > m24):  # 1-3 line catches up to 2-4 line: converge
                continue
            pats.append({"dir": 1, "completion": p5["confirm"], "p1": p1, "p2": p2,
                         "p3": p3, "p4": p4, "p5": p5,
                         "m13": m13, "b13": b13, "m24": m24, "b24": b24,
                         "mepa": mepa, "bepa": bepa})
        elif kinds == ["H", "L", "H", "L", "H"]:
            if not (p3["price"] > p1["price"] and p4["price"] > p2["price"]):
                continue
            if not (p5["price"] > m13 * p5["idx"] + b13):
                continue
            if not (m13 < m24):  # 1-3 line catches up to 2-4 line: converge
                continue
            pats.append({"dir": -1, "completion": p5["confirm"], "p1": p1, "p2": p2,
                         "p3": p3, "p4": p4, "p5": p5,
                         "m13": m13, "b13": b13, "m24": m24, "b24": b24,
                         "mepa": mepa, "bepa": bepa})
    return pats


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    atr_v = df["atr14"].to_numpy()
    pivots = _zigzag_pivots(df["h"].to_numpy(), df["l"].to_numpy(), atr_v)
    pats = _wolfe_patterns(pivots)
    line13 = np.full(n, np.nan)
    line24 = np.full(n, np.nan)
    epa = np.full(n, np.nan)
    bullish = np.zeros(n)
    bearish = np.zeros(n)
    complete = np.full(n, np.nan)
    for pat in pats:
        start = pat["completion"]
        end = n
        # Pattern stays the "most recent" until the next pattern completes.
        nxt = [q["completion"] for q in pats if q["completion"] > start]
        if nxt:
            end = min(nxt)
        idx = np.arange(start, end)
        line13[start:end] = pat["m13"] * idx + pat["b13"]
        line24[start:end] = pat["m24"] * idx + pat["b24"]
        epa[start:end] = pat["mepa"] * idx + pat["bepa"]
        if pat["dir"] == 1:
            bullish[start:end] = 1.0
        else:
            bearish[start:end] = 1.0
        complete[start:end] = float(start)
    df["ww_line13"] = line13
    df["ww_line24"] = line24
    df["ww_epa"] = epa
    df["ww_bullish"] = bullish
    df["ww_bearish"] = bearish
    df["ww_complete"] = complete
    return df
