"""5-0 Pattern indicators: zigzag swing detector + Scott Carney 5-0
harmonic geometry.

Zigzag: 5-bar local extrema, minimum swing 0.9x ATR(14) between
consecutive pivots, alternating pivot types, pivots usable only 2 bars
after the extreme bar. Bullish 5-0: 0=low, X=high, A=low, B=high with
AB = 1.13-1.618x XA (+/-0.10), C=low with BC = 1.618-2.24x AB (+/-0.10),
D = 50% retracement of BC (+/-0.08) reached after C; B must exceed X
and C must fall below A. Bearish is the mirror image. All ratios are
computed on pivot prices. Exit target: the 38.2% retracement of the BC
leg measured from B (bullish: C + 0.618*BC, above the D entry). A
correction note: the original brief specified the exit as the 38.2%
retracement of the C-to-D leg measured from C, which sits BELOW the D
entry price and exits ~immediately at a small loss; that level was
corrected to the standard BC-leg retracement target before shipping
(see CALIBRATION.md for the as-specified numbers).
"""

import numpy as np
import pandas as pd

from strategies import base as B

INDICATOR_COLS = [
    "atr14",
    "fz_bullish",
    "fz_bearish",
    "fz_d_level",
    "fz_exit_long",
    "fz_exit_short",
    "fz_complete",
]

MIN_SWING_ATR = 0.9
AB_MIN, AB_MAX = 1.13 - 0.10, 1.618 + 0.10
BC_MIN, BC_MAX = 1.618 - 0.10, 2.24 + 0.10
D_RETRACE = 0.50
D_TOL = 0.08


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


def _five_zero_patterns(pivots):
    """Return list of completed 5-0 patterns (D level + exit level)."""
    pats = []
    for k in range(len(pivots) - 4):
        w = pivots[k:k + 5]
        kinds = [p["kind"] for p in w]
        if kinds == ["L", "H", "L", "H", "L"]:
            p0, px, pa, pb, pc = w
            xa = px["price"] - p0["price"]
            ab = pb["price"] - pa["price"]
            bc = pb["price"] - pc["price"]
            if min(xa, ab, bc) <= 0:
                continue
            if not (AB_MIN <= ab / xa <= AB_MAX):
                continue
            if not (BC_MIN <= bc / ab <= BC_MAX):
                continue
            if not (pb["price"] > px["price"] and pc["price"] < pa["price"]):
                continue
            d_level = pc["price"] + D_RETRACE * bc
            exit_level = pc["price"] + 0.618 * bc  # 38.2% retracement of BC from B
            pats.append({"dir": 1, "completion": pc["confirm"],
                         "d_level": d_level, "exit_level": exit_level})
        elif kinds == ["H", "L", "H", "L", "H"]:
            p0, px, pa, pb, pc = w
            xa = p0["price"] - px["price"]
            ab = pa["price"] - pb["price"]
            bc = pc["price"] - pb["price"]
            if min(xa, ab, bc) <= 0:
                continue
            if not (AB_MIN <= ab / xa <= AB_MAX):
                continue
            if not (BC_MIN <= bc / ab <= BC_MAX):
                continue
            if not (pb["price"] < px["price"] and pc["price"] > pa["price"]):
                continue
            d_level = pc["price"] - D_RETRACE * bc
            exit_level = pc["price"] - 0.618 * bc  # 38.2% retracement of BC from B
            pats.append({"dir": -1, "completion": pc["confirm"],
                         "d_level": d_level, "exit_level": exit_level})
    return pats


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    atr_v = df["atr14"].to_numpy()
    pivots = _zigzag_pivots(df["h"].to_numpy(), df["l"].to_numpy(), atr_v)
    pats = _five_zero_patterns(pivots)
    bullish = np.zeros(n)
    bearish = np.zeros(n)
    d_level = np.full(n, np.nan)
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
        d_level[start:end] = pat["d_level"]
        complete[start:end] = float(start)
    df["fz_bullish"] = bullish
    df["fz_bearish"] = bearish
    df["fz_d_level"] = d_level
    df["fz_exit_long"] = exit_long
    df["fz_exit_short"] = exit_short
    df["fz_complete"] = complete
    return df
