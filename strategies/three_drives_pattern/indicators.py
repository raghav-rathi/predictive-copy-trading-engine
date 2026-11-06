"""Three Drives Pattern indicators: zigzag swing detector + harmonic
Three Drives geometry.

Zigzag: 5-bar local extrema, minimum swing 0.9x ATR(14) between
consecutive pivots, alternating pivot types, pivots usable only 2 bars
after the extreme bar. Bullish Three Drives: three successive lower
pivot lows D1, D2, D3 separated by pullback highs; each pullback
retraces 0.618 or 0.786 (+/-0.08) of the prior drive and each new drive
extends 1.272 or 1.618 (+/-0.10) of the prior pullback; drive lengths
in bars must be symmetric (each within 0.5x-2x of the first).
Bearish is the mirror image. All ratios are computed on pivot closes
(pivot high/low prices).
"""

import numpy as np
import pandas as pd

from strategies import base as B

INDICATOR_COLS = [
    "atr14",
    "td_bullish",
    "td_bearish",
    "td_d3",
    "td_exit_long",
    "td_exit_short",
    "td_complete",
]

MIN_SWING_ATR = 0.9
RETRACE_LEVELS = (0.618, 0.786)
RETRACE_TOL = 0.08
EXTENSION_LEVELS = (1.272, 1.618)
EXTENSION_TOL = 0.10


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


def _near(value, levels, tol):
    return any(abs(value - lv) <= tol for lv in levels)


def _three_drives_patterns(pivots):
    """Return list of completed Three Drives patterns."""
    pats = []
    for k in range(len(pivots) - 5):
        w = pivots[k:k + 6]
        kinds = [p["kind"] for p in w]
        if kinds == ["H", "L", "H", "L", "H", "L"]:
            h0, d1, p1, d2, p2, d3 = w
            if not (d2["price"] < d1["price"] and d3["price"] < d2["price"]):
                continue
            drive1 = h0["price"] - d1["price"]
            pb1 = p1["price"] - d1["price"]
            drive2 = p1["price"] - d2["price"]
            pb2 = p2["price"] - d2["price"]
            drive3 = p2["price"] - d3["price"]
            if min(drive1, pb1, drive2, pb2, drive3) <= 0:
                continue
            if not _near(pb1 / drive1, RETRACE_LEVELS, RETRACE_TOL):
                continue
            if not _near(drive2 / pb1, EXTENSION_LEVELS, EXTENSION_TOL):
                continue
            if not _near(pb2 / drive2, RETRACE_LEVELS, RETRACE_TOL):
                continue
            if not _near(drive3 / pb2, EXTENSION_LEVELS, EXTENSION_TOL):
                continue
            len1 = d1["idx"] - h0["idx"]
            len2 = d2["idx"] - p1["idx"]
            len3 = d3["idx"] - p2["idx"]
            if not (0.5 * len1 <= len2 <= 2.0 * len1 and 0.5 * len1 <= len3 <= 2.0 * len1):
                continue
            exit_level = d3["price"] + 0.618 * (h0["price"] - d3["price"])
            pats.append({"dir": 1, "completion": d3["confirm"], "d3": d3["price"],
                         "exit_level": exit_level})
        elif kinds == ["L", "H", "L", "H", "L", "H"]:
            l0, d1, p1, d2, p2, d3 = w
            if not (d2["price"] > d1["price"] and d3["price"] > d2["price"]):
                continue
            drive1 = d1["price"] - l0["price"]
            pb1 = d1["price"] - p1["price"]
            drive2 = d2["price"] - p1["price"]
            pb2 = d2["price"] - p2["price"]
            drive3 = d3["price"] - p2["price"]
            if min(drive1, pb1, drive2, pb2, drive3) <= 0:
                continue
            if not _near(pb1 / drive1, RETRACE_LEVELS, RETRACE_TOL):
                continue
            if not _near(drive2 / pb1, EXTENSION_LEVELS, EXTENSION_TOL):
                continue
            if not _near(pb2 / drive2, RETRACE_LEVELS, RETRACE_TOL):
                continue
            if not _near(drive3 / pb2, EXTENSION_LEVELS, EXTENSION_TOL):
                continue
            len1 = d1["idx"] - l0["idx"]
            len2 = d2["idx"] - p1["idx"]
            len3 = d3["idx"] - p2["idx"]
            if not (0.5 * len1 <= len2 <= 2.0 * len1 and 0.5 * len1 <= len3 <= 2.0 * len1):
                continue
            exit_level = d3["price"] - 0.618 * (d3["price"] - l0["price"])
            pats.append({"dir": -1, "completion": d3["confirm"], "d3": d3["price"],
                         "exit_level": exit_level})
    return pats


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    atr_v = df["atr14"].to_numpy()
    pivots = _zigzag_pivots(df["h"].to_numpy(), df["l"].to_numpy(), atr_v)
    pats = _three_drives_patterns(pivots)
    bullish = np.zeros(n)
    bearish = np.zeros(n)
    d3_col = np.full(n, np.nan)
    exit_long = np.full(n, np.nan)
    exit_short = np.full(n, np.nan)
    complete = np.full(n, np.nan)
    for pat in pats:
        start = pat["completion"]
        end = n
        nxt = [q["completion"] for q in pats if q["completion"] > start]
        if nxt:
            end = min(nxt)
        if pat["dir"] == 1:
            bullish[start:end] = 1.0
            exit_long[start:end] = pat["exit_level"]
        else:
            bearish[start:end] = 1.0
            exit_short[start:end] = pat["exit_level"]
        d3_col[start:end] = pat["d3"]
        complete[start:end] = float(start)
    df["td_bullish"] = bullish
    df["td_bearish"] = bearish
    df["td_d3"] = d3_col
    df["td_exit_long"] = exit_long
    df["td_exit_short"] = exit_short
    df["td_complete"] = complete
    return df
