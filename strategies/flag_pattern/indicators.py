"""Bull / bear flag: sharp pole, tight consolidation, breakout.

The textbook flag (Bulkowski): a near-vertical pole (here: a move of
at least 3x ATR(14) within 12 bars), then a short, tight consolidation
that retraces no more than 60% of the pole and spans no more than
1.5x ATR in range, lasting 5–15 bars — then a breakout in the pole's
direction. No zigzag here: the pole/consolidation detector is a
causal state machine over closes.

Columns:
    flag_dir   -- +1 while a bull flag is armed, -1 bear flag, else 0
    flag_level -- consolidation high (bull) / low (bear) while armed
    atr        -- Wilder ATR(14)

Armed state persists until the breakout (handled in signals.py) or
invalidation (price breaks the consolidation's far side by more than
0.5x ATR). No lookahead: every decision reads closes through bar i.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_N = 14
POLE_MIN_ATR = 3.0   # pole must move at least 3x ATR
POLE_MAX_BARS = 12   # ...within at most 12 bars
CONS_MIN_BARS = 5    # consolidation must last at least 5 bars
CONS_MAX_BARS = 15   # ...and at most 15
CONS_MAX_RANGE_ATR = 1.5  # consolidation range cap
MAX_RETRACE = 0.60   # consolidation may retrace at most 60% of the pole
FAIL_ATR = 0.5       # far-side break that invalidates the flag


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    o = df["o"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    atr = B.atr(df["h"], df["l"], df["c"], ATR_N).to_numpy(dtype=float)

    dir_col = np.zeros(n, dtype=int)
    level_col = np.full(n, np.nan)

    state = "idle"  # idle | consolidating | armed
    pole_dir = 0
    pole_top = float("nan")
    pole_bottom = float("nan")
    pole_size = 0.0
    cons_start = -1
    cons_high = float("nan")
    cons_low = float("nan")

    for i in range(n):
        a = atr[i] if np.isfinite(atr[i]) else 0.0
        if state == "idle":
            # A pole is a COMPLETED sharp move: require the last two bars
            # to have stalled, so a steady trend cannot trigger mid-pole
            # (the rise would then invalidate its own consolidation).
            stalled = (
                i >= 2
                and abs(c[i] - c[i - 1]) <= 0.5 * a
                and abs(c[i - 1] - c[i - 2]) <= 0.5 * a
            )
            if a > 0 and stalled:
                for w in range(3, POLE_MAX_BARS + 1):
                    if i - w < 0:
                        break
                    up = c[i] - c[i - w]
                    dn = c[i - w] - c[i]
                    if up >= POLE_MIN_ATR * a:
                        state = "consolidating"
                        pole_dir = 1
                        pole_top = max(c[i - w:i + 1])
                        pole_bottom = c[i - w]
                        pole_size = up
                        cons_start = i
                        cons_high = h[i]
                        cons_low = l[i]
                        break
                    if dn >= POLE_MIN_ATR * a:
                        state = "consolidating"
                        pole_dir = -1
                        pole_top = c[i - w]
                        pole_bottom = min(c[i - w:i + 1])
                        pole_size = dn
                        cons_start = i
                        cons_high = h[i]
                        cons_low = l[i]
                        break
        elif state == "consolidating":
            cons_high = max(cons_high, h[i])
            cons_low = min(cons_low, l[i])
            bars = i - cons_start
            retrace = (pole_top - c[i]) / pole_size if pole_dir == 1 else (c[i] - pole_bottom) / pole_size
            if retrace > MAX_RETRACE or (cons_high - cons_low) > CONS_MAX_RANGE_ATR * a:
                state = "idle"
            elif bars >= CONS_MIN_BARS:
                state = "armed"
            elif bars > CONS_MAX_BARS:
                state = "idle"
        elif state == "armed":
            if pole_dir == 1 and c[i] < cons_low - FAIL_ATR * a:
                state = "idle"
            elif pole_dir == -1 and c[i] > cons_high + FAIL_ATR * a:
                state = "idle"

        if state == "armed":
            dir_col[i] = pole_dir
            level_col[i] = cons_high if pole_dir == 1 else cons_low
        else:
            dir_col[i] = 0
            level_col[i] = np.nan

    df["flag_dir"] = dir_col
    df["flag_level"] = level_col
    df["atr"] = atr
    return df
