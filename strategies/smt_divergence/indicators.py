"""ICT Smart Money Technique (SMT) divergence indicators (BTC vs ETH).

``build_merged_frame(traded_df, ref_df)`` aligns the traded coin and
the reference coin on ``t`` (inner join) into one frame with the
traded OHLCV in ``o/h/l/c/v`` and the reference OHLCV in
``o_ref/h_ref/l_ref/c_ref``.

``add_indicators`` runs causal 5-bar pivots on BOTH series: a swing
high at centre j iff h[j] is the max of h[j-2..j+2] (strictly above
its left neighbour); a swing low iff l[j] is the min of l[j-2..j+2].
A pivot is recorded at its CONFIRMATION bar (centre+2), never at the
centre bar, via an explicit loop.

Bullish SMT divergence: the traded coin prints a new swing low below
its prior swing low (lower low) while the reference coin's most
recent swing low is HIGHER than its prior swing low (higher low),
and the two lows are within 10 bars of each other (centre distance)
-> divergence armed. Entry is the first close above the traded
coin's prior swing high (structure shift) within 20 bars of arming.
Bearish SMT is the mirror (traded higher high, reference lower high,
entry on a close below the traded coin's prior swing low).

Columns:
    t_swing_high / t_swing_low -- traded confirmed swing levels
    r_swing_high / r_swing_low -- reference confirmed swing levels
    smt_state -- 0 none, 1 divergence armed (either side)
    smt_side  -- +1 bearish armed, -1 bullish armed, 0 none
    smt_level -- structure-shift trigger level while armed, else NaN
    long_trigger / short_trigger -- True only on the entry bar
    last_bull_div_low / last_bear_div_high -- divergence swing
        extreme recorded at the entry trigger, forward-filled
        (invalidation level for the exit rule)
    atr -- Wilder ATR(14) of the traded coin, for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT = 2
LOW_GAP_MAX = 10    # max centre distance between the two divergence lows/highs
ENTRY_EXPIRY = 20   # bars after arming during which the shift may trigger

INDICATOR_COLS = ["t_swing_high", "t_swing_low", "r_swing_high",
                  "r_swing_low", "smt_state", "smt_level",
                  "long_trigger", "short_trigger", "atr"]


def build_merged_frame(traded_df: pd.DataFrame,
                       ref_df: pd.DataFrame) -> pd.DataFrame:
    """Align traded and reference 1h frames on t (inner join)."""
    m = traded_df[["t", "o", "h", "l", "c", "v"]].merge(
        ref_df[["t", "o", "h", "l", "c"]],
        on="t", suffixes=("", "_ref")).sort_values("t")
    return m.reset_index(drop=True)


def _pivot_lists(h, l, n):
    """Causal 5-bar pivot confirmation.

    Returns (highs, lows): lists of (level, centre) in confirmation
    order, plus per-bar arrays of the newly confirmed pivot (or None).
    """
    highs: list[tuple[float, int]] = []
    lows: list[tuple[float, int]] = []
    new_sh = [None] * n
    new_sl = [None] * n
    for i in range(n):
        j = i - PIVOT
        if j >= PIVOT:
            if h[j] == h[j - PIVOT:j + PIVOT + 1].max() and h[j] > h[j - 1]:
                new_sh[i] = (float(h[j]), j)
                highs.append((float(h[j]), j))
            if l[j] == l[j - PIVOT:j + PIVOT + 1].min() and l[j] < l[j - 1]:
                new_sl[i] = (float(l[j]), j)
                lows.append((float(l[j]), j))
    return highs, lows, new_sh, new_sl


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    hr = df["h_ref"].to_numpy(dtype=float)
    lr = df["l_ref"].to_numpy(dtype=float)
    n = len(df)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)

    t_highs, t_lows, _, _ = _pivot_lists(h, l, n)
    r_highs, r_lows, _, _ = _pivot_lists(hr, lr, n)
    # Index the pivot lists by confirmation bar for the main loop.
    t_high_by_bar: dict[int, tuple[float, int]] = {}
    t_low_by_bar: dict[int, tuple[float, int]] = {}
    r_high_by_bar: dict[int, tuple[float, int]] = {}
    r_low_by_bar: dict[int, tuple[float, int]] = {}
    for lvl, j in t_highs:
        t_high_by_bar[j + PIVOT] = (lvl, j)
    for lvl, j in t_lows:
        t_low_by_bar[j + PIVOT] = (lvl, j)
    for lvl, j in r_highs:
        r_high_by_bar[j + PIVOT] = (lvl, j)
    for lvl, j in r_lows:
        r_low_by_bar[j + PIVOT] = (lvl, j)

    t_sh = np.full(n, np.nan)
    t_sl = np.full(n, np.nan)
    r_sh = np.full(n, np.nan)
    r_sl = np.full(n, np.nan)
    smt_state = np.zeros(n, dtype=int)
    smt_side = np.zeros(n, dtype=int)
    smt_level = np.full(n, np.nan)
    long_trig = np.zeros(n, dtype=bool)
    short_trig = np.zeros(n, dtype=bool)
    last_bull_div = np.full(n, np.nan)
    last_bear_div = np.full(n, np.nan)

    last_t_sh = last_t_sl = last_r_sh = last_r_sl = np.nan
    # Confirmed swing lists, in confirmation order.
    t_lows_seen: list[tuple[float, int]] = []
    t_highs_seen: list[tuple[float, int]] = []
    r_lows_seen: list[tuple[float, int]] = []
    r_highs_seen: list[tuple[float, int]] = []
    cur_bull_div = np.nan
    cur_bear_div = np.nan

    # Bullish armed state.
    b_armed = False
    b_div_low = np.nan
    b_trigger = np.nan
    b_armed_idx = -1
    b_key = None
    # Bearish armed state (mirror).
    s_armed = False
    s_div_high = np.nan
    s_trigger = np.nan
    s_armed_idx = -1
    s_key = None

    for i in range(n):
        if i in t_high_by_bar:
            last_t_sh = t_high_by_bar[i][0]
            t_highs_seen.append(t_high_by_bar[i])
        if i in t_low_by_bar:
            last_t_sl = t_low_by_bar[i][0]
            t_lows_seen.append(t_low_by_bar[i])
        if i in r_high_by_bar:
            last_r_sh = r_high_by_bar[i][0]
            r_highs_seen.append(r_high_by_bar[i])
        if i in r_low_by_bar:
            last_r_sl = r_low_by_bar[i][0]
            r_lows_seen.append(r_low_by_bar[i])

        # ---- bullish arming ----
        if not b_armed and len(t_lows_seen) >= 2 and len(r_lows_seen) >= 2:
            (t_prev, t_prev_j), (t_new, t_new_j) = t_lows_seen[-2], t_lows_seen[-1]
            (r_prev, r_prev_j), (r_new, r_new_j) = r_lows_seen[-2], r_lows_seen[-1]
            key = (t_new_j, r_new_j)
            if (t_new < t_prev and r_new > r_prev
                    and abs(t_new_j - r_new_j) <= LOW_GAP_MAX
                    and key != b_key and t_highs_seen):
                b_armed = True
                b_div_low = t_new
                b_trigger = t_highs_seen[-1][0]
                b_armed_idx = i
                b_key = key
        # ---- bearish arming (mirror) ----
        if not s_armed and len(t_highs_seen) >= 2 and len(r_highs_seen) >= 2:
            (t_prev, t_prev_j), (t_new, t_new_j) = t_highs_seen[-2], t_highs_seen[-1]
            (r_prev, r_prev_j), (r_new, r_new_j) = r_highs_seen[-2], r_highs_seen[-1]
            key = (t_new_j, r_new_j)
            if (t_new > t_prev and r_new < r_prev
                    and abs(t_new_j - r_new_j) <= LOW_GAP_MAX
                    and key != s_key and t_lows_seen):
                s_armed = True
                s_div_high = t_new
                s_trigger = t_lows_seen[-1][0]
                s_armed_idx = i
                s_key = key

        # ---- bullish armed: track / expire / invalidate / trigger ----
        if b_armed:
            if i in t_low_by_bar and t_low_by_bar[i][0] < b_div_low:
                b_div_low = t_low_by_bar[i][0]
            if i in t_high_by_bar:
                b_trigger = t_high_by_bar[i][0]
            if i - b_armed_idx > ENTRY_EXPIRY:
                b_armed = False
            elif c[i] < b_div_low:
                b_armed = False
            elif c[i] > b_trigger:
                long_trig[i] = True
                cur_bull_div = b_div_low
                b_armed = False
        # ---- bearish armed (mirror) ----
        if s_armed:
            if i in t_high_by_bar and t_high_by_bar[i][0] > s_div_high:
                s_div_high = t_high_by_bar[i][0]
            if i in t_low_by_bar:
                s_trigger = t_low_by_bar[i][0]
            if i - s_armed_idx > ENTRY_EXPIRY:
                s_armed = False
            elif c[i] > s_div_high:
                s_armed = False
            elif c[i] < s_trigger:
                short_trig[i] = True
                cur_bear_div = s_div_high
                s_armed = False

        t_sh[i] = last_t_sh
        t_sl[i] = last_t_sl
        r_sh[i] = last_r_sh
        r_sl[i] = last_r_sl
        smt_state[i] = 1 if (b_armed or s_armed) else 0
        if b_armed and s_armed:
            smt_side[i] = 0
            smt_level[i] = np.nan
        elif b_armed:
            smt_side[i] = -1
            smt_level[i] = b_trigger
        elif s_armed:
            smt_side[i] = 1
            smt_level[i] = s_trigger
        else:
            smt_side[i] = 0
            smt_level[i] = np.nan
        last_bull_div[i] = cur_bull_div
        last_bear_div[i] = cur_bear_div

    df["t_swing_high"] = t_sh
    df["t_swing_low"] = t_sl
    df["r_swing_high"] = r_sh
    df["r_swing_low"] = r_sl
    df["smt_state"] = smt_state
    df["smt_side"] = smt_side
    df["smt_level"] = smt_level
    df["long_trigger"] = long_trig
    df["short_trigger"] = short_trig
    df["last_bull_div_low"] = last_bull_div
    df["last_bear_div_high"] = last_bear_div
    return df
