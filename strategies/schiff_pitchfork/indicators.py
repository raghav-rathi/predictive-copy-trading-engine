"""Schiff pitchfork median-line pullback indicators.

A Schiff pitchfork (a variant of the Andrews pitchfork) is drawn
from three consecutive confirmed pivots A, B, C. Unlike the
standard Andrews fork, whose median line starts at A itself, the
Schiff fork's median line starts at the midpoint of A and B:
the anchor is (bar of A, (A + B) / 2) and the line runs through
the midpoint of B-C (midBC bar, midBC price). That shifted anchor
is the whole point of the Schiff variant — it makes the fork
flatter and the median line sit closer to price, so pullbacks to
the median line happen sooner and more often than with a standard
Andrews fork (see strategies/andrews_pitchfork, which anchors at
A). The parallels pass through B and C and share the median
line's slope.

Pivots are confirmed 10-bar pivots: a swing high at centre j iff
h[j] is the max of the 10 bars h[j-7..j+2] (strictly above its
left neighbour, to break ties); a swing low iff l[j] is the min
of l[j-7..j+2]. A pivot is recorded at its confirmation bar
(centre+2), never at the centre bar. Three consecutive pivots
form a set: low-high-low (bullish) or high-low-high (bearish).
Only the most recent set per side is active; a set expires 200
bars after its C pivot confirms; a newly completed triple of the
same side re-anchors.

Bullish set: long when price touches the median line from above
(the bar's low is within 0.5 ATR(14) of the median-line value)
and then closes back above the median line (the touch bar itself
counts if it closes back above; otherwise the touch arms the
setup for the next 5 bars). Bearish is the mirror (touch from
below, close back below).

Columns:
    atr -- Wilder ATR(14)
    pf_bull_median / pf_bull_upper / pf_bull_lower -- bullish
        Schiff median line and the parallels through B (upper)
        and C (lower), NaN when no bullish set is active
    pf_bear_median / pf_bear_upper / pf_bear_lower -- bearish
        set: median line and the parallels through B (lower)
        and C (upper)
    schiff_state -- 0 none, 1 set active, 2 touch armed
        (max over the two sides)
    schiff_side -- +1 bullish set furthest along, -1 bearish, 0 none
    long_trigger / short_trigger -- True only on the entry bar

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT_BACK = 7   # pivot window is bars [j-7, j+2] (10 bars)
PIVOT_FWD = 2    # confirmation at centre+2
TOUCH_ATR = 0.5
ARM_BARS = 5
SET_EXPIRY = 200

INDICATOR_COLS = [
    "atr",
    "pf_bull_median",
    "pf_bull_upper",
    "pf_bull_lower",
    "pf_bear_median",
    "pf_bear_upper",
    "pf_bear_lower",
    "schiff_state",
]


def _set_geometry(a_bar, a_price, b_bar, b_price, c_bar, c_price):
    """Schiff anchor + slope for a pivot triple (A, B, C)."""
    anchor_bar = float(a_bar)
    anchor_price = (a_price + b_price) / 2.0
    mid_bar = (b_bar + c_bar) / 2.0
    mid_price = (b_price + c_price) / 2.0
    slope = (mid_price - anchor_price) / (mid_bar - anchor_bar)
    return anchor_bar, anchor_price, slope


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    atr_v = df["atr"].to_numpy(dtype=float)

    bull_med = np.full(n, np.nan)
    bull_up = np.full(n, np.nan)
    bull_lo = np.full(n, np.nan)
    bear_med = np.full(n, np.nan)
    bear_up = np.full(n, np.nan)
    bear_lo = np.full(n, np.nan)
    schiff_state = np.zeros(n, dtype=int)
    schiff_side = np.zeros(n, dtype=int)
    long_trig = np.zeros(n, dtype=bool)
    short_trig = np.zeros(n, dtype=bool)

    pivots = []  # dicts: bar (centre), price, kind 'H'/'L', confirm bar
    # Active sets: dict or None.
    bull = None
    bear = None
    bull_armed_until = -1
    bear_armed_until = -1

    for i in range(n):
        # ---- pivot confirmation for centre j = i-2 ----
        new_pivot = None
        j = i - PIVOT_FWD
        if j >= PIVOT_BACK:
            if (h[j] == h[j - PIVOT_BACK:j + PIVOT_FWD + 1].max()
                    and h[j] > h[j - 1]):
                new_pivot = {"bar": j, "price": float(h[j]), "kind": "H", "confirm": i}
            elif (l[j] == l[j - PIVOT_BACK:j + PIVOT_FWD + 1].min()
                    and l[j] < l[j - 1]):
                new_pivot = {"bar": j, "price": float(l[j]), "kind": "L", "confirm": i}
        if new_pivot is not None:
            if pivots and pivots[-1]["kind"] == new_pivot["kind"]:
                last = pivots[-1]
                if ((new_pivot["kind"] == "H" and new_pivot["price"] > last["price"])
                        or (new_pivot["kind"] == "L" and new_pivot["price"] < last["price"])):
                    pivots[-1] = new_pivot
            else:
                pivots.append(new_pivot)
            # A newly completed triple re-anchors that side's set.
            if len(pivots) >= 3:
                a, b, cc = pivots[-3], pivots[-2], pivots[-1]
                kinds = (a["kind"], b["kind"], cc["kind"])
                if kinds == ("L", "H", "L"):
                    anchor_bar, anchor_price, slope = _set_geometry(
                        a["bar"], a["price"], b["bar"], b["price"],
                        cc["bar"], cc["price"])
                    bull = {
                        "anchor_bar": anchor_bar, "anchor_price": anchor_price,
                        "slope": slope, "b_bar": float(b["bar"]),
                        "b_price": b["price"], "c_bar": float(cc["bar"]),
                        "c_price": cc["price"],
                        "expiry": cc["confirm"] + SET_EXPIRY,
                    }
                    bull_armed_until = -1
                elif kinds == ("H", "L", "H"):
                    anchor_bar, anchor_price, slope = _set_geometry(
                        a["bar"], a["price"], b["bar"], b["price"],
                        cc["bar"], cc["price"])
                    bear = {
                        "anchor_bar": anchor_bar, "anchor_price": anchor_price,
                        "slope": slope, "b_bar": float(b["bar"]),
                        "b_price": b["price"], "c_bar": float(cc["bar"]),
                        "c_price": cc["price"],
                        "expiry": cc["confirm"] + SET_EXPIRY,
                    }
                    bear_armed_until = -1

        # ---- expire stale sets ----
        if bull is not None and i > bull["expiry"]:
            bull = None
            bull_armed_until = -1
        if bear is not None and i > bear["expiry"]:
            bear = None
            bear_armed_until = -1

        # ---- bullish median-line touch / entry ----
        bull_active = bull is not None
        bear_active = bear is not None
        bull_armed = False
        bear_armed = False
        if bull_active:
            med = bull["anchor_price"] + bull["slope"] * (i - bull["anchor_bar"])
            bull_med[i] = med
            bull_up[i] = bull["b_price"] + bull["slope"] * (i - bull["b_bar"])
            bull_lo[i] = bull["c_price"] + bull["slope"] * (i - bull["c_bar"])
            if np.isfinite(atr_v[i]) and abs(l[i] - med) <= TOUCH_ATR * atr_v[i]:
                bull_armed_until = i + ARM_BARS
            if i <= bull_armed_until and c[i] > med:
                long_trig[i] = True
                bull_armed_until = -1
            bull_armed = i <= bull_armed_until
        if bear_active:
            med = bear["anchor_price"] + bear["slope"] * (i - bear["anchor_bar"])
            bear_med[i] = med
            bear_up[i] = bear["c_price"] + bear["slope"] * (i - bear["c_bar"])
            bear_lo[i] = bear["b_price"] + bear["slope"] * (i - bear["b_bar"])
            if np.isfinite(atr_v[i]) and abs(h[i] - med) <= TOUCH_ATR * atr_v[i]:
                bear_armed_until = i + ARM_BARS
            if i <= bear_armed_until and c[i] < med:
                short_trig[i] = True
                bear_armed_until = -1
            bear_armed = i <= bear_armed_until

        # ---- record this bar ----
        if bull_armed or bear_armed:
            schiff_state[i] = 2
        elif bull_active or bear_active:
            schiff_state[i] = 1
        else:
            schiff_state[i] = 0
        if bull_armed and not bear_armed:
            schiff_side[i] = 1
        elif bear_armed and not bull_armed:
            schiff_side[i] = -1
        elif bull_active and not bear_active:
            schiff_side[i] = 1
        elif bear_active and not bull_active:
            schiff_side[i] = -1
        else:
            schiff_side[i] = 0

    df["pf_bull_median"] = bull_med
    df["pf_bull_upper"] = bull_up
    df["pf_bull_lower"] = bull_lo
    df["pf_bear_median"] = bear_med
    df["pf_bear_upper"] = bear_up
    df["pf_bear_lower"] = bear_lo
    df["schiff_state"] = schiff_state
    df["schiff_side"] = schiff_side
    df["long_trigger"] = long_trig
    df["short_trigger"] = short_trig
    return df
