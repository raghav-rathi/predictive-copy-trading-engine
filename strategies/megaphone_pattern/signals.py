"""Megaphone Pattern signals (broadening formation).

Pattern: 3 successive higher highs AND 3 successive lower lows, alternating,
each swing expanding on the previous by >= 0.5x ATR(14) (prior-bar ATR).
Only the most recent completed pattern counts; a pattern is consumed once
it triggers an entry, and a new pattern must complete before re-arming.

Entry long: after the 3rd lower low is in (last pivot is a low), close above
the most recent swing high. Entry short: after the 3rd higher high is in
(last pivot is a high), close below the most recent swing low.
Exit long: close below the pattern midline (midpoint of the last swing high
and last swing low at completion). Exit short is the mirror.

Swing pivots arrive already lagged 2 bars (see indicators.py), and the ATR
threshold uses the prior bar's ATR, so no comparison uses current-bar
information beyond the close itself.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    sh = df["swing_high"].to_numpy(dtype=float)
    sl = df["swing_low"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    atr = df["atr14"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pivots = []  # (idx, "H"/"L", price), alternating, extreme kept
    consumed = set()
    armed = None  # "long" | "short" | None
    midline = np.nan
    pattern_seen = False

    def _add_pivot(idx, kind, price):
        if pivots and pivots[-1][1] == kind:
            # Same kind twice in a row: keep only the more extreme one.
            if kind == "H":
                if price > pivots[-1][2]:
                    pivots[-1] = (idx, kind, price)
            else:
                if price < pivots[-1][2]:
                    pivots[-1] = (idx, kind, price)
            return
        pivots.append((idx, kind, price))

    for i in range(n):
        if np.isfinite(sh[i]):
            _add_pivot(i, "H", float(sh[i]))
        if np.isfinite(sl[i]):
            _add_pivot(i, "L", float(sl[i]))

        # Pattern check on the last 6 pivots.
        if len(pivots) >= 6 and i > 0 and np.isfinite(atr[i - 1]) and atr[i - 1] > 0:
            last6 = pivots[-6:]
            kinds = "".join(p[1] for p in last6)
            if kinds in ("HLHLHL", "LHLHLH"):
                highs = [p[2] for p in last6 if p[1] == "H"]
                lows = [p[2] for p in last6 if p[1] == "L"]
                sig = tuple(p[0] for p in last6)
                if sig not in consumed:
                    thr = 0.5 * atr[i - 1]
                    expanding = (
                        highs[1] - highs[0] >= thr
                        and highs[2] - highs[1] >= thr
                        and lows[0] - lows[1] >= thr
                        and lows[1] - lows[2] >= thr
                        and highs[0] < highs[1] < highs[2]
                        and lows[0] > lows[1] > lows[2]
                    )
                    if expanding:
                        armed = "long" if last6[-1][1] == "L" else "short"
                        midline = (highs[-1] + lows[-1]) / 2.0
                        pattern_seen = True

        last_high = pivots[-1][2] if pivots and pivots[-1][1] == "H" else None
        # Most recent swing high / low regardless of order.
        highs_so_far = [p[2] for p in pivots if p[1] == "H"]
        lows_so_far = [p[2] for p in pivots if p[1] == "L"]
        recent_high = highs_so_far[-1] if highs_so_far else None
        recent_low = lows_so_far[-1] if lows_so_far else None

        if armed == "long" and recent_high is not None and c[i] > recent_high:
            le[i] = True
            consumed.add(tuple(p[0] for p in pivots[-6:]))
            armed = None
        elif armed == "short" and recent_low is not None and c[i] < recent_low:
            se[i] = True
            consumed.add(tuple(p[0] for p in pivots[-6:]))
            armed = None

        if pattern_seen and np.isfinite(midline):
            lx[i] = c[i] < midline
            sx[i] = c[i] > midline

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
