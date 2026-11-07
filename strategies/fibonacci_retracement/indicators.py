"""Fibonacci retracement indicators: golden-zone pullback entries.

Swings are consecutive 5-bar fractal pivots (middle bar extreme vs 2 bars
each side, alternating types, minimum swing 0.9x ATR(14), usable only 2
bars after the extreme bar). An impulse leg A->B must be >= 1.0x ATR(14).

Uptrend swing (A = low, B = high): the golden zone is the 38.2%-61.8%
retracement of A->B. The setup arms when the pullback first touches the
zone (low <= 38.2% level); it stays armed until a close beyond A
(invalidation) or a close reaching B (target reached without entry).
Downtrend is the mirror image. State-machine notes: a new pivot low
after B is the pullback itself and never flips the swing; a newer
same-direction swing replaces the active one only while it is untouched
(most recent impulse wins); once the zone is touched the swing is locked
so the armed setup's levels cannot shift under it; opposite-direction
swings only activate when no swing is active.
"""

import numpy as np
import pandas as pd

from strategies import base as B

INDICATOR_COLS = [
    "atr14",
    "fib_dir",
    "fib_a",
    "fib_b",
    "fib_zone_lo",
    "fib_zone_hi",
    "fib_touched",
    "fib_swing_id",
]

MIN_SWING_ATR = 0.9
MIN_LEG_ATR = 1.0
RETRACE_LO = 0.382
RETRACE_HI = 0.618


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


def _swing_events(pivots, atr_v):
    """Consecutive-pivot swings with leg >= 1.0x ATR(14).

    Each event: dir (+1 uptrend: A low -> B high; -1 downtrend), A, B,
    completion bar (B's confirm bar, used as the swing id).
    """
    events = []
    for k in range(len(pivots) - 1):
        a_piv, b_piv = pivots[k], pivots[k + 1]
        a = atr_v[b_piv["idx"]] if np.isfinite(atr_v[b_piv["idx"]]) else 0.0
        leg = abs(b_piv["price"] - a_piv["price"])
        if leg < MIN_LEG_ATR * a:
            continue
        if b_piv["kind"] == "H":
            events.append({"dir": 1, "a": a_piv["price"], "b": b_piv["price"],
                           "completion": b_piv["confirm"]})
        else:
            events.append({"dir": -1, "a": a_piv["price"], "b": b_piv["price"],
                           "completion": b_piv["confirm"]})
    return events


def _zone(swing):
    """(zone_lo, zone_hi): the 38.2%-61.8% retracement band of A->B."""
    a, b = swing["a"], swing["b"]
    leg = b - a
    if swing["dir"] == 1:
        return b - RETRACE_HI * leg, b - RETRACE_LO * leg
    return b + RETRACE_LO * (-leg), b + RETRACE_HI * (-leg)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    c = df["c"].to_numpy()
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    atr_v = df["atr14"].to_numpy()
    pivots = _fractal_pivots(h, l, atr_v)
    events = _swing_events(pivots, atr_v)
    events_by_bar = {}
    for ev in events:
        events_by_bar.setdefault(ev["completion"], []).append(ev)
    direction = np.zeros(n)
    a_col = np.full(n, np.nan)
    b_col = np.full(n, np.nan)
    zlo_col = np.full(n, np.nan)
    zhi_col = np.full(n, np.nan)
    touched_col = np.zeros(n)
    swing_id = np.full(n, np.nan)
    active = None  # dict(dir, a, b, completion, touched)
    for i in range(n):
        # (a) New swing completes: activate, or replace an untouched
        # same-direction swing; opposite-direction swings wait for a gap.
        for ev in events_by_bar.get(i, []):
            if active is None:
                active = dict(ev, touched=False)
            elif ev["dir"] == active["dir"] and not active["touched"]:
                active = dict(ev, touched=False)
        if active is not None:
            zlo, zhi = _zone(active)
            # (b) First touch of the zone locks the swing.
            if active["dir"] == 1 and l[i] <= zhi:
                active["touched"] = True
            elif active["dir"] == -1 and h[i] >= zlo:
                active["touched"] = True
            # (c) Emit this bar's columns.
            direction[i] = float(active["dir"])
            a_col[i] = active["a"]
            b_col[i] = active["b"]
            zlo_col[i] = zlo
            zhi_col[i] = zhi
            touched_col[i] = 1.0 if active["touched"] else 0.0
            swing_id[i] = float(active["completion"])
            # (d) Clear for the next bar on invalidation / target reached.
            if active["dir"] == 1 and (c[i] < active["a"] or c[i] >= active["b"]):
                active = None
            elif active["dir"] == -1 and (c[i] > active["a"] or c[i] <= active["b"]):
                active = None
    df["fib_dir"] = direction
    df["fib_a"] = a_col
    df["fib_b"] = b_col
    df["fib_zone_lo"] = zlo_col
    df["fib_zone_hi"] = zhi_col
    df["fib_touched"] = touched_col
    df["fib_swing_id"] = swing_id
    return df
