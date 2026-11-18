"""Sperandeo 2B reversal indicators.

2B top (short): (a) a new 20-bar high, (b) a pullback of at least 5
bars with no new high, (c) a retest bar that closes above that high,
(d) a later bar that closes below the retest bar's low -> failed
retest, short entry on that close. 2B bottom (long) is the mirror.

State machine (causal loop, one pass over bars, no forward shifts):
  phase 0 idle -> new 20-bar extreme arms the pattern (phase 1)
  phase 1 pullback -> after 5 bars elapsed since the extreme bar,
          phase 2 (armed for the retest). A fresh 20-bar extreme
          while in phase 1 re-arms on the new extreme.
  phase 2 armed -> the first bar closing beyond the extreme is the
          retest bar (phase 3, retest level = retest bar's low for
          tops / high for bottoms). A fresh 20-bar extreme while
          armed re-arms instead (the retest check runs first, so a
          bar that IS the retest is never mistaken for a re-arm).
          No retest within 28 bars of the extreme bar disarms.
  phase 3 awaiting failure -> a close beyond the retest level in the
          failing direction fires the trigger for that bar only and
          resets the machine. A fresh 20-bar extreme while awaiting
          failure re-arms on the new extreme. No failure within 20
          bars of the retest bar disarms.

Columns:
    new_high_20 -- h[i] > max(h[i-20..i-1]) (previous 20 bars only)
    new_low_20  -- l[i] < min(l[i-20..i-1])
    armed_top / armed_bottom -- phase 2 or 3 (pullback done, pattern live)
    retest_level -- retest bar's low (tops) / high (bottoms) while in phase 3
    await_top / await_bottom -- phase 3 (waiting for the failure close)
    short_trigger / long_trigger -- True only on the failure-confirmation bar
    last_top_extreme / last_bottom_extreme -- most recent arming extreme,
        forward-filled (invalidation level for the exit rule)
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

LOOKBACK = 20
PULLBACK_MIN = 5
RETEST_WINDOW = 28  # 8-bar max pullback + 20 bars to retest, from the extreme bar
FAILURE_WINDOW = 20  # bars after the retest bar to confirm the failure

INDICATOR_COLS = ["new_high_20", "new_low_20", "armed_top",
                  "armed_bottom", "retest_level", "atr"]


def add_indicators(df: pd.DataFrame, lookback: int = LOOKBACK,
                   pullback_min: int = PULLBACK_MIN) -> pd.DataFrame:
    df = df.copy()
    h = df["h"]
    l = df["l"]
    c = df["c"]
    prev_high = h.rolling(lookback, min_periods=lookback).max().shift(1)
    prev_low = l.rolling(lookback, min_periods=lookback).min().shift(1)
    df["new_high_20"] = (h > prev_high).fillna(False).astype(bool)
    df["new_low_20"] = (l < prev_low).fillna(False).astype(bool)
    df["atr"] = B.atr(h, l, c, 14)

    n = len(df)
    hv = h.to_numpy(dtype=float)
    lv = l.to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    new_hi = df["new_high_20"].to_numpy()
    new_lo = df["new_low_20"].to_numpy()

    armed_top = np.zeros(n, dtype=bool)
    armed_bot = np.zeros(n, dtype=bool)
    await_top = np.zeros(n, dtype=bool)
    await_bot = np.zeros(n, dtype=bool)
    retest_level = np.full(n, np.nan)
    short_trig = np.zeros(n, dtype=bool)
    long_trig = np.zeros(n, dtype=bool)
    last_top = np.full(n, np.nan)
    last_bot = np.full(n, np.nan)

    # Top (short) state: phase 0 idle, 1 pullback, 2 armed, 3 awaiting failure.
    t_phase = 0
    t_ext = np.nan
    t_idx = -1
    t_retest_low = np.nan
    t_retest_idx = -1
    cur_top = np.nan
    # Bottom (long) state, mirrored.
    b_phase = 0
    b_ext = np.nan
    b_idx = -1
    b_retest_high = np.nan
    b_retest_idx = -1
    cur_bot = np.nan

    for i in range(n):
        # ---- top side ----
        if t_phase == 3:
            if cv[i] < t_retest_low:
                short_trig[i] = True
                t_phase = 0
                t_retest_low = np.nan
            elif new_hi[i]:
                t_ext, t_idx, t_phase = hv[i], i, 1
                cur_top = hv[i]
            elif i - t_retest_idx > FAILURE_WINDOW:
                t_phase = 0
                t_retest_low = np.nan
        elif t_phase == 2:
            if cv[i] > t_ext:
                t_retest_low, t_retest_idx, t_phase = lv[i], i, 3
            elif new_hi[i]:
                t_ext, t_idx, t_phase = hv[i], i, 1
                cur_top = hv[i]
            elif i - t_idx > RETEST_WINDOW:
                t_phase = 0
        elif t_phase == 1:
            if new_hi[i]:
                t_ext, t_idx = hv[i], i
                cur_top = hv[i]
            elif i - t_idx >= pullback_min:
                t_phase = 2
        else:
            if new_hi[i]:
                t_ext, t_idx, t_phase = hv[i], i, 1
                cur_top = hv[i]
        # ---- bottom side (mirror) ----
        if b_phase == 3:
            if cv[i] > b_retest_high:
                long_trig[i] = True
                b_phase = 0
                b_retest_high = np.nan
            elif new_lo[i]:
                b_ext, b_idx, b_phase = lv[i], i, 1
                cur_bot = lv[i]
            elif i - b_retest_idx > FAILURE_WINDOW:
                b_phase = 0
                b_retest_high = np.nan
        elif b_phase == 2:
            if cv[i] < b_ext:
                b_retest_high, b_retest_idx, b_phase = hv[i], i, 3
            elif new_lo[i]:
                b_ext, b_idx, b_phase = lv[i], i, 1
                cur_bot = lv[i]
            elif i - b_idx > RETEST_WINDOW:
                b_phase = 0
        elif b_phase == 1:
            if new_lo[i]:
                b_ext, b_idx = lv[i], i
                cur_bot = lv[i]
            elif i - b_idx >= pullback_min:
                b_phase = 2
        else:
            if new_lo[i]:
                b_ext, b_idx, b_phase = lv[i], i, 1
                cur_bot = lv[i]
        # ---- record this bar ----
        armed_top[i] = t_phase in (2, 3)
        armed_bot[i] = b_phase in (2, 3)
        await_top[i] = t_phase == 3
        await_bot[i] = b_phase == 3
        if t_phase == 3:
            retest_level[i] = t_retest_low
        elif b_phase == 3:
            retest_level[i] = b_retest_high
        last_top[i] = cur_top
        last_bot[i] = cur_bot

    df["armed_top"] = armed_top
    df["armed_bottom"] = armed_bot
    df["await_top"] = await_top
    df["await_bottom"] = await_bot
    df["retest_level"] = retest_level
    df["short_trigger"] = short_trig
    df["long_trigger"] = long_trig
    df["last_top_extreme"] = last_top
    df["last_bottom_extreme"] = last_bot
    return df
