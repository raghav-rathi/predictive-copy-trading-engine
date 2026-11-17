"""Swing-structure breakout indicators.

Swing-structure breakout on 5-bar pivots: a swing high is a high
strictly greater than the 2 bars on each side; a swing low is a
low strictly lower than the 2 bars on each side.

A pivot is only *known* once the 2 bars to its right have closed,
so the pivot is recorded at its confirmation bar (center + 2).
Every value on bar i therefore uses data through bar i's close
only — no lookahead. The most recent confirmed swing high / swing
low is carried forward (last_swing_high / last_swing_low).

Long:  close breaks above the last swing high AND the last two
       swing lows are ascending (the most recent swing low is
       higher than the one before it — higher lows).
Short: close breaks below the last swing low AND the last two
       swing highs are descending (lower highs).

Exits are the opposite structure break:
    long exit:  close breaks below the last swing low
    short exit: close breaks above the last swing high

Columns:

    is_swing_high, is_swing_low -- bool, pivot confirmed on this bar
    swing_high, swing_low       -- pivot price when confirmed, else NaN
    last_swing_high, last_swing_low
    prev_swing_high, prev_swing_low
    lows_ascending, highs_descending -- bool, last two pivots
    long_breakout               -- close > last swing high
    short_breakout              -- close < last swing low
    atr                         -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT_LEFT = 2
PIVOT_RIGHT = 2

INDICATOR_COLS = ["is_swing_high", "is_swing_low", "swing_high",
                  "swing_low", "last_swing_high", "last_swing_low",
                  "prev_swing_high", "prev_swing_low",
                  "lows_ascending", "highs_descending",
                  "long_breakout", "short_breakout", "atr"]


def _confirmed_pivots(h: np.ndarray, l: np.ndarray):
    """Pivot values placed at their confirmation bar (center + 2)."""
    n = len(h)
    sh = np.full(n, np.nan)
    sl = np.full(n, np.nan)
    is_sh = np.zeros(n, dtype=bool)
    is_sl = np.zeros(n, dtype=bool)
    for i in range(PIVOT_LEFT, n - PIVOT_RIGHT):
        if (h[i] > h[i - 2] and h[i] > h[i - 1]
                and h[i] > h[i + 1] and h[i] > h[i + 2]):
            sh[i + PIVOT_RIGHT] = h[i]
            is_sh[i + PIVOT_RIGHT] = True
        if (l[i] < l[i - 2] and l[i] < l[i - 1]
                and l[i] < l[i + 1] and l[i] < l[i + 2]):
            sl[i + PIVOT_RIGHT] = l[i]
            is_sl[i + PIVOT_RIGHT] = True
    return sh, sl, is_sh, is_sl


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    sh, sl, is_sh, is_sl = _confirmed_pivots(h, l)

    last_sh = np.full(n, np.nan)
    last_sl = np.full(n, np.nan)
    prev_sh = np.full(n, np.nan)
    prev_sl = np.full(n, np.nan)
    lows_asc = np.zeros(n, dtype=bool)
    highs_desc = np.zeros(n, dtype=bool)
    sh_hist: list[float] = []
    sl_hist: list[float] = []
    for i in range(n):
        if is_sh[i]:
            sh_hist.append(float(sh[i]))
        if is_sl[i]:
            sl_hist.append(float(sl[i]))
        if sh_hist:
            last_sh[i] = sh_hist[-1]
            if len(sh_hist) >= 2:
                prev_sh[i] = sh_hist[-2]
        if sl_hist:
            last_sl[i] = sl_hist[-1]
            if len(sl_hist) >= 2:
                prev_sl[i] = sl_hist[-2]
        lows_asc[i] = len(sl_hist) >= 2 and sl_hist[-1] > sl_hist[-2]
        highs_desc[i] = len(sh_hist) >= 2 and sh_hist[-1] < sh_hist[-2]

    df["is_swing_high"] = is_sh
    df["is_swing_low"] = is_sl
    df["swing_high"] = sh
    df["swing_low"] = sl
    df["last_swing_high"] = last_sh
    df["last_swing_low"] = last_sl
    df["prev_swing_high"] = prev_sh
    df["prev_swing_low"] = prev_sl
    df["lows_ascending"] = lows_asc
    df["highs_descending"] = highs_desc
    df["long_breakout"] = (
        (df["c"] > df["last_swing_high"]).fillna(False).astype(bool)
    )
    df["short_breakout"] = (
        (df["c"] < df["last_swing_low"]).fillna(False).astype(bool)
    )
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
