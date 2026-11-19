"""Livermore pivotal-point / Market Key indicators.

Jesse Livermore's pivotal-point system (How to Trade in Stocks,
1940): a stock (here: a coin) consolidates in a narrow range, then
breaks out of the range on expanding volume (the "pivotal point"),
reacts back toward the pivot on contracting volume without
violating it (the "natural reaction"), and then resumes in the
break direction. The resumption close is the entry.

Consolidation: a 20-bar window whose range (max high - min low
over the window) is < 0.6x the median 20-bar range of the prior
100 bars (narrow range). The bull pivot is that window's high,
the bear pivot its low; the pivot is frozen when the window
completes. A newly completed consolidation replaces the active
pivot (and resets any in-progress setup on that side).

Bullish sequence (bearish is the mirror):
  1. Break: close above the bull pivot with volume > 1.25x the
     20-bar mean volume.
  2. Natural reaction: within the next 10 bars, a bar whose close
     is below the break bar's close (a pullback), whose low stays
     above the pivot, and whose volume is below the 20-bar mean
     (contraction). The reaction high is the highest high from the
     break bar through the reaction bar.
  3. Resumption: a close above the reaction high with volume above
     the 20-bar mean -> long_trigger.

A close back below the bull pivot (long) / above the bear pivot
(short) before resumption invalidates the setup (Livermore's
danger signal). A reaction that never comes within 10 bars, or a
resumption that never comes within 20 bars of the reaction, also
resets the setup (staleness guards, a priori, see CALIBRATION.md).

Columns:
    range20 -- 20-bar window range (max high - min low)
    range20_med100 -- median of the prior 100 range20 values
    narrow -- range20 < 0.6 * range20_med100
    vol_mean20 -- 20-bar mean volume
    bull_pivot / bear_pivot -- active pivot levels, forward-filled
        (NaN before the first consolidation completes)
    liv_state -- 0 none, 1 break confirmed, 2 reaction armed
        (max over the two sides)
    liv_side -- +1 bullish setup furthest along, -1 bearish, 0 none
    long_trigger / short_trigger -- True only on the entry bar
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

WINDOW = 20
MEDIAN_LOOKBACK = 100
NARROW_MULT = 0.6
BREAK_VOL_MULT = 1.25
REACTION_BARS = 10
RESUME_EXPIRY = 20

INDICATOR_COLS = [
    "range20",
    "range20_med100",
    "narrow",
    "vol_mean20",
    "bull_pivot",
    "bear_pivot",
    "liv_state",
    "atr",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)
    n = len(df)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)

    range20 = (
        df["h"].rolling(WINDOW, min_periods=WINDOW).max()
        - df["l"].rolling(WINDOW, min_periods=WINDOW).min()
    )
    range20_med = range20.rolling(MEDIAN_LOOKBACK, min_periods=MEDIAN_LOOKBACK).median().shift(1)
    narrow = (range20 < NARROW_MULT * range20_med).fillna(False).to_numpy()
    vol_mean20 = df["v"].rolling(WINDOW, min_periods=WINDOW).mean().to_numpy(dtype=float)

    df["range20"] = range20
    df["range20_med100"] = range20_med
    df["narrow"] = narrow
    df["vol_mean20"] = vol_mean20

    bull_pivot = np.full(n, np.nan)
    bear_pivot = np.full(n, np.nan)
    liv_state = np.zeros(n, dtype=int)
    liv_side = np.zeros(n, dtype=int)
    long_trig = np.zeros(n, dtype=bool)
    short_trig = np.zeros(n, dtype=bool)

    cur_bull = np.nan
    cur_bear = np.nan
    # Long (bullish) machine: 0 idle/armed, 1 break, 2 reaction armed.
    l_stage = 0
    l_break_idx = -1
    l_break_close = np.nan
    l_react_high = np.nan
    l_react_idx = -1
    # Short (bearish) machine (mirror).
    s_stage = 0
    s_break_idx = -1
    s_break_close = np.nan
    s_react_low = np.nan
    s_react_idx = -1

    for i in range(n):
        # ---- a completed consolidation replaces the active pivot ----
        if narrow[i] and i >= WINDOW - 1:
            cur_bull = float(h[i - WINDOW + 1:i + 1].max())
            cur_bear = float(l[i - WINDOW + 1:i + 1].min())
            l_stage = 0
            s_stage = 0

        vm = vol_mean20[i]
        vol_ok = np.isfinite(vm) and vm > 0

        # ---- bullish machine ----
        if l_stage == 0:
            if (np.isfinite(cur_bull) and vol_ok
                    and c[i] > cur_bull and v[i] > BREAK_VOL_MULT * vm):
                l_stage = 1
                l_break_idx = i
                l_break_close = c[i]
                l_react_high = h[i]
        elif l_stage == 1:
            if i - l_break_idx > REACTION_BARS:
                l_stage = 0
            elif c[i] < cur_bull:
                l_stage = 0  # danger signal: fell back below the pivot
            elif (c[i] < l_break_close and l[i] > cur_bull
                    and vol_ok and v[i] < vm):
                l_stage = 2
                l_react_idx = i
                l_react_high = max(l_react_high, h[i])
            else:
                l_react_high = max(l_react_high, h[i])
        else:  # l_stage == 2
            if c[i] > l_react_high and vol_ok and v[i] > vm:
                long_trig[i] = True
                l_stage = 0
            elif c[i] < cur_bull:
                l_stage = 0
            elif i - l_react_idx > RESUME_EXPIRY:
                l_stage = 0

        # ---- bearish machine (mirror) ----
        if s_stage == 0:
            if (np.isfinite(cur_bear) and vol_ok
                    and c[i] < cur_bear and v[i] > BREAK_VOL_MULT * vm):
                s_stage = 1
                s_break_idx = i
                s_break_close = c[i]
                s_react_low = l[i]
        elif s_stage == 1:
            if i - s_break_idx > REACTION_BARS:
                s_stage = 0
            elif c[i] > cur_bear:
                s_stage = 0  # danger signal: back above the pivot
            elif (c[i] > s_break_close and h[i] < cur_bear
                    and vol_ok and v[i] < vm):
                s_stage = 2
                s_react_idx = i
                s_react_low = min(s_react_low, l[i])
            else:
                s_react_low = min(s_react_low, l[i])
        else:  # s_stage == 2
            if c[i] < s_react_low and vol_ok and v[i] > vm:
                short_trig[i] = True
                s_stage = 0
            elif c[i] > cur_bear:
                s_stage = 0
            elif i - s_react_idx > RESUME_EXPIRY:
                s_stage = 0

        # ---- record this bar ----
        bull_pivot[i] = cur_bull
        bear_pivot[i] = cur_bear
        liv_state[i] = max(l_stage, s_stage)
        if l_stage > s_stage:
            liv_side[i] = 1
        elif s_stage > l_stage:
            liv_side[i] = -1
        else:
            liv_side[i] = 0

    df["bull_pivot"] = bull_pivot
    df["bear_pivot"] = bear_pivot
    df["liv_state"] = liv_state
    df["liv_side"] = liv_side
    df["long_trigger"] = long_trig
    df["short_trigger"] = short_trig
    return df
