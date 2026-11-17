"""Demark-style trendline breakout indicators.

Swing pivots: 10-bar pivots — a swing high is a high strictly
greater than the 5 bars on each side; a swing low is a low
strictly less than the 5 bars on each side.

A pivot formed at bar i is only CONFIRMED at bar i+5, once the
5 bars to its right are known. The shipped columns expose only
confirmed pivots (``swing_high`` / ``swing_low`` are True on the
confirmation bar, i.e. 5 bars after the pivot bar), so no signal
can ever use an unconfirmed pivot.

Trendlines (recomputed causally, only pivots confirmed by bar i):
    downtrend line -- straight line through the last two confirmed
                      swing highs, extrapolated to bar i.
    uptrend line   -- straight line through the last two confirmed
                      swing lows, extrapolated to bar i.

A line exists only once two pivots of that kind have been
confirmed; before that the line column is NaN.

Columns:

    swing_high     -- bool, a swing-high pivot confirmed on this bar
    swing_low      -- bool, a swing-low pivot confirmed on this bar
    downtrend_line -- value of the downtrend line at this bar
    uptrend_line   -- value of the uptrend line at this bar
    atr            -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only (a pivot's confirmation lag is implemented honestly — the
pivot is not visible until 5 bars after it forms).
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT_SIDE = 5
CONFIRM_LAG = 5

INDICATOR_COLS = ["swing_high", "swing_low", "downtrend_line",
                  "uptrend_line", "atr"]


def _raw_pivots(h: pd.Series, l: pd.Series):
    """Centered pivots: True at the pivot bar itself (NOT causal —
    used internally only; callers must apply the confirmation lag)."""
    hv = h.to_numpy(dtype=float)
    lv = l.to_numpy(dtype=float)
    n = len(hv)
    ph = np.zeros(n, dtype=bool)
    pl = np.zeros(n, dtype=bool)
    for i in range(PIVOT_SIDE, n - PIVOT_SIDE):
        if hv[i] > hv[i - PIVOT_SIDE:i].max() and hv[i] > hv[i + 1:i + 1 + PIVOT_SIDE].max():
            ph[i] = True
        if lv[i] < lv[i - PIVOT_SIDE:i].min() and lv[i] < lv[i + 1:i + 1 + PIVOT_SIDE].min():
            pl[i] = True
    return ph, pl


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    hv = df["h"].to_numpy(dtype=float)
    lv = df["l"].to_numpy(dtype=float)

    ph_raw, pl_raw = _raw_pivots(df["h"], df["l"])
    # Confirmation lag: a pivot at bar i is known at bar i + 5.
    swing_high = np.zeros(n, dtype=bool)
    swing_low = np.zeros(n, dtype=bool)
    if n > CONFIRM_LAG:
        swing_high[CONFIRM_LAG:] = ph_raw[:-CONFIRM_LAG]
        swing_low[CONFIRM_LAG:] = pl_raw[:-CONFIRM_LAG]

    down = np.full(n, np.nan)
    up = np.full(n, np.nan)
    last_highs: list[tuple[int, float]] = []
    last_lows: list[tuple[int, float]] = []
    for t in range(n):
        if swing_high[t]:
            # The pivot confirmed on bar t formed at bar t - 5.
            last_highs.append((t - CONFIRM_LAG, hv[t - CONFIRM_LAG]))
            last_highs = last_highs[-2:]
        if swing_low[t]:
            last_lows.append((t - CONFIRM_LAG, lv[t - CONFIRM_LAG]))
            last_lows = last_lows[-2:]
        if len(last_highs) == 2:
            (i1, v1), (i2, v2) = last_highs
            slope = (v2 - v1) / (i2 - i1)
            down[t] = v2 + slope * (t - i2)
        if len(last_lows) == 2:
            (i1, v1), (i2, v2) = last_lows
            slope = (v2 - v1) / (i2 - i1)
            up[t] = v2 + slope * (t - i2)

    df["swing_high"] = swing_high
    df["swing_low"] = swing_low
    df["downtrend_line"] = down
    df["uptrend_line"] = up
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
