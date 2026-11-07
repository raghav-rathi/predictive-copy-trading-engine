"""1-2-3 Reversal indicators: Joe Ross 1-2-3 pattern on 5-bar fractal pivots.

Pivots are 5-bar local extrema (middle bar extreme vs 2 bars each side),
alternating types, minimum swing 0.9x ATR(14) between consecutive pivots,
usable only 2 bars after the extreme bar (no lookahead).

Bullish 1-2-3: point 1 = fractal low (end of a decline), point 2 =
fractal high of the first rally off point 1, point 3 = pullback low
holding above point 1. The 1->2 leg must be >= 1.0x ATR(14); if point 3
falls to/below point 1 the pattern is void. The pattern completes on a
close above point 2. Bearish is the mirror image. While a pattern is
active, a newer confirmed pullback low below the current point 3 (but
still above point 1) updates point 3 to the deeper pullback low.
"""

import numpy as np
import pandas as pd

from strategies import base as B

INDICATOR_COLS = [
    "atr14",
    "otr_bullish",
    "otr_bearish",
    "otr_bull_p1",
    "otr_bull_p2",
    "otr_bull_p3",
    "otr_bull_complete",
    "otr_bear_p1",
    "otr_bear_p2",
    "otr_bear_p3",
    "otr_bear_complete",
]

MIN_SWING_ATR = 0.9
MIN_LEG_ATR = 1.0


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


def _patterns(pivots, atr_v):
    """Return list of 1-2-3 patterns: dicts with dir, p1, p2, p3, completion."""
    pats = []
    for k in range(len(pivots) - 2):
        w = pivots[k:k + 3]
        kinds = [p["kind"] for p in w]
        a = atr_v[w[1]["idx"]] if np.isfinite(atr_v[w[1]["idx"]]) else 0.0
        if kinds == ["L", "H", "L"]:
            p1, p2, p3 = w
            leg = p2["price"] - p1["price"]
            if leg < MIN_LEG_ATR * a:
                continue
            if not (p3["price"] > p1["price"]):
                continue
            pats.append({"dir": 1, "p1": p1, "p2": p2, "p3": p3,
                         "completion": p3["confirm"]})
        elif kinds == ["H", "L", "H"]:
            p1, p2, p3 = w
            leg = p1["price"] - p2["price"]
            if leg < MIN_LEG_ATR * a:
                continue
            if not (p3["price"] < p1["price"]):
                continue
            pats.append({"dir": -1, "p1": p1, "p2": p2, "p3": p3,
                         "completion": p3["confirm"]})
    return pats


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy()
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    atr_v = df["atr14"].to_numpy()
    pivots = _fractal_pivots(df["h"].to_numpy(), df["l"].to_numpy(), atr_v)
    pats = _patterns(pivots, atr_v)
    bullish = np.zeros(n)
    bearish = np.zeros(n)
    bull_p1 = np.full(n, np.nan)
    bull_p2 = np.full(n, np.nan)
    bull_p3 = np.full(n, np.nan)
    bull_complete = np.full(n, np.nan)
    bear_p1 = np.full(n, np.nan)
    bear_p2 = np.full(n, np.nan)
    bear_p3 = np.full(n, np.nan)
    bear_complete = np.full(n, np.nan)
    # Two independent state machines (one per direction): a pattern is
    # active from its completion bar until it completes (close through
    # point 2) or voids (close through point 1). A newer pattern of the
    # same direction replaces the old one. While active, a newer confirmed
    # pullback extreme below the current point 3 (but still beyond point 1)
    # updates point 3.
    active = {1: None, -1: None}  # dir -> dict(p1, p2, p3, completion)
    pat_by_completion = {}
    for pat in pats:
        pat_by_completion.setdefault(pat["completion"], []).append(pat)
    piv_by_confirm = {}
    for pv in pivots:
        piv_by_confirm.setdefault(pv["confirm"], []).append(pv)
    for i in range(n):
        for pat in pat_by_completion.get(i, []):
            active[pat["dir"]] = {
                "p1": pat["p1"]["price"],
                "p2": pat["p2"]["price"],
                "p3": pat["p3"]["price"],
                "completion": pat["completion"],
            }
        for d in (1, -1):
            act = active[d]
            if act is None:
                continue
            for pv in piv_by_confirm.get(i, []):
                if d == 1 and pv["kind"] == "L" and act["p1"] < pv["price"] < act["p3"]:
                    act["p3"] = pv["price"]
                elif d == -1 and pv["kind"] == "H" and act["p3"] < pv["price"] < act["p1"]:
                    act["p3"] = pv["price"]
            if d == 1:
                if c[i] <= act["p1"]:
                    active[d] = None
                else:
                    bullish[i] = 1.0
                    bull_p1[i] = act["p1"]
                    bull_p2[i] = act["p2"]
                    bull_p3[i] = act["p3"]
                    bull_complete[i] = float(act["completion"])
                    if c[i] > act["p2"]:
                        active[d] = None  # completed on this close
            else:
                if c[i] >= act["p1"]:
                    active[d] = None
                else:
                    bearish[i] = 1.0
                    bear_p1[i] = act["p1"]
                    bear_p2[i] = act["p2"]
                    bear_p3[i] = act["p3"]
                    bear_complete[i] = float(act["completion"])
                    if c[i] < act["p2"]:
                        active[d] = None  # completed on this close
    df["otr_bullish"] = bullish
    df["otr_bearish"] = bearish
    df["otr_bull_p1"] = bull_p1
    df["otr_bull_p2"] = bull_p2
    df["otr_bull_p3"] = bull_p3
    df["otr_bull_complete"] = bull_complete
    df["otr_bear_p1"] = bear_p1
    df["otr_bear_p2"] = bear_p2
    df["otr_bear_p3"] = bear_p3
    df["otr_bear_complete"] = bear_complete
    return df
