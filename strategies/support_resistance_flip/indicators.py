"""Break-and-retest / role-reversal indicators.

Source: break-and-retest with confirmation (Prometheus Markets;
HowToTrade "what is retest"): a level that has been tested
repeatedly, breaks, and is then retested from the other side and
holds, has flipped role — old resistance becomes support (and
vice versa). The entry is on the retest-hold bar, not on the
break itself.

Levels: 5-bar pivot swing highs/lows (a swing high is a high
strictly greater than the 2 bars on each side; swing low mirror),
with pivot centre inside the trailing 50-bar window. A pivot is
only *known* once the 2 bars to its right have closed, so it is
recorded at its confirmation bar (centre + 2) — no lookahead.

A level counts only if price touched it at least twice: bars in
the trailing 50-bar window (through the break bar) whose low is
within 0.5x ATR(14) of the level, using the break bar's ATR.

Break: a close crosses beyond the level (close above a
resistance level having closed at/below it the prior bar, or
close below a support level having closed at/above it the prior
bar). The break opens a pending setup for that level.

Retest: within the next 20 bars after the break bar, a bar whose
low comes within 0.5x ATR of the level (that bar's ATR) AND
whose close is back on the flipped side of the level — above it
for a broken resistance (bullish hold), below it for a broken
support (bearish hold). Long/short entry fires on that
retest-hold bar, the level becomes the active flipped level, and
the pending setup is consumed. If no retest within 20 bars the
setup expires.

Exits: long exit on a close back below the flipped level; short
exit on a close back above it. The flipped level is carried in
flip_long_level / flip_short_level until the exit fires.

State rules (documented decisions, see CALIBRATION.md):
  * If a new qualifying break occurs while a setup in the same
    direction is still pending, the newest break replaces it.
  * A pending setup is NOT invalidated by a close back across
    the level during the retest window; it stays pending until
    a retest-hold fires or the 20 bars expire.
  * If a second retest-hold entry fires while a flipped level
    is already active in the same direction, the active level
    updates to the newest entry's level.

Columns:

    is_swing_high, is_swing_low -- bool, pivot confirmed on this bar
    swing_high, swing_low       -- pivot price when confirmed, else NaN
    pending_bull_level, pending_bear_level -- level awaiting retest
    flip_long_level, flip_short_level -- active flipped level
    retest_bull, retest_bear    -- bool, retest-hold entry bar
    atr                         -- Wilder ATR(14)

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT_LEFT = 2
PIVOT_RIGHT = 2
LEVEL_WINDOW = 50
TOUCH_MULT = 0.5
TOUCH_MIN = 2
RETEST_BARS = 20

INDICATOR_COLS = ["is_swing_high", "is_swing_low", "swing_high",
                  "swing_low", "pending_bull_level",
                  "pending_bear_level", "flip_long_level",
                  "flip_short_level", "retest_bull", "retest_bear",
                  "atr"]


def _confirmed_pivots(h: np.ndarray, l: np.ndarray):
    """Pivot values placed at their confirmation bar (centre + 2)."""
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


def add_indicators(df: pd.DataFrame, window: int = LEVEL_WINDOW,
                   touch_mult: float = TOUCH_MULT,
                   touch_min: int = TOUCH_MIN,
                   retest_bars: int = RETEST_BARS) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    atr_v = B.atr(df["h"], df["l"], df["c"], 14).to_numpy(dtype=float)
    sh, sl, is_sh, is_sl = _confirmed_pivots(h, l)

    pending_bull_level = np.full(n, np.nan)
    pending_bear_level = np.full(n, np.nan)
    flip_long_level = np.full(n, np.nan)
    flip_short_level = np.full(n, np.nan)
    retest_bull = np.zeros(n, dtype=bool)
    retest_bear = np.zeros(n, dtype=bool)

    # (centre_idx, kind 'R'/'S', level); pruned to the window each bar.
    pivots: list[tuple[int, str, float]] = []
    pending_bull: tuple[float, int] | None = None  # (level, break_idx)
    pending_bear: tuple[float, int] | None = None
    active_long: float | None = None
    active_short: float | None = None

    for i in range(n):
        if is_sh[i]:
            pivots.append((i - PIVOT_RIGHT, "R", float(sh[i])))
        if is_sl[i]:
            pivots.append((i - PIVOT_RIGHT, "S", float(sl[i])))
        pivots = [p for p in pivots if p[0] >= i - window]

        # Expire pending setups older than the retest window.
        if pending_bull is not None and i - pending_bull[1] > retest_bars:
            pending_bull = None
        if pending_bear is not None and i - pending_bear[1] > retest_bars:
            pending_bear = None

        a = atr_v[i]

        # Retest-hold: only on bars after the break bar.
        if pending_bull is not None and i > pending_bull[1] and np.isfinite(a):
            lvl = pending_bull[0]
            if abs(l[i] - lvl) <= touch_mult * a and c[i] > lvl:
                retest_bull[i] = True
                active_long = lvl
                pending_bull = None
        if pending_bear is not None and i > pending_bear[1] and np.isfinite(a):
            lvl = pending_bear[0]
            if abs(l[i] - lvl) <= touch_mult * a and c[i] < lvl:
                retest_bear[i] = True
                active_short = lvl
                pending_bear = None

        # Break detection: close crosses a qualifying level.
        if i > 0 and np.isfinite(a):
            lo = max(0, i - window)
            cands_bull: list[float] = []
            cands_bear: list[float] = []
            for (_ctr, kind, lvl) in pivots:
                touches = int(
                    np.sum(np.abs(l[lo:i + 1] - lvl) <= touch_mult * a)
                )
                if touches < touch_min:
                    continue
                if kind == "R" and c[i] > lvl and c[i - 1] <= lvl:
                    cands_bull.append(lvl)
                elif kind == "S" and c[i] < lvl and c[i - 1] >= lvl:
                    cands_bear.append(lvl)
            if cands_bull:
                # Nearest broken level to the close is the relevant one.
                lvl = min(cands_bull, key=lambda x: abs(x - c[i]))
                pending_bull = (lvl, i)
            if cands_bear:
                lvl = min(cands_bear, key=lambda x: abs(x - c[i]))
                pending_bear = (lvl, i)

        # Record the flipped levels as they stand this bar (before
        # clearing on an exit, so signals.py can see the exit bar).
        flip_long_level[i] = active_long if active_long is not None else np.nan
        flip_short_level[i] = active_short if active_short is not None else np.nan
        if active_long is not None and c[i] < active_long:
            active_long = None
        if active_short is not None and c[i] > active_short:
            active_short = None

        pending_bull_level[i] = (
            pending_bull[0] if pending_bull is not None else np.nan
        )
        pending_bear_level[i] = (
            pending_bear[0] if pending_bear is not None else np.nan
        )

    df["is_swing_high"] = is_sh
    df["is_swing_low"] = is_sl
    df["swing_high"] = sh
    df["swing_low"] = sl
    df["pending_bull_level"] = pending_bull_level
    df["pending_bear_level"] = pending_bear_level
    df["flip_long_level"] = flip_long_level
    df["flip_short_level"] = flip_short_level
    df["retest_bull"] = retest_bull
    df["retest_bear"] = retest_bear
    df["atr"] = atr_v
    return df
