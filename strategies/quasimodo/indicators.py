"""Quasimodo / over-and-under reversal indicators.

Causal 5-bar pivots: a swing high at centre j iff h[j] is the max
of h[j-2..j+2] (strictly above its left neighbour, to break ties);
a swing low iff l[j] is the min of l[j-2..j+2]. A pivot is recorded
at its CONFIRMATION bar (centre+2), never at the centre bar, via an
explicit loop — no forward-shifted comparisons anywhere in the
signal path.

Bearish QM (short), five swings in order: (1) H1 swing high;
(2) L1 following swing low; (3) H2 higher swing high (the head);
(4) a close below L1 (the break / change of character);
(5) a retracement back above L1 that stays below the head H2 and
forms a swing low RL (the shoulder); entry on a close below RL.
Bullish QM is the mirror (L1, H1, L2 lower low = head, close above
H1, retracement back below H1 staying above the head, swing high
RH, entry on a close above RH).

State machine per side (stages): 1 first swing, 2 second swing,
3 head formed, 4 break confirmed, 5 shoulder armed. While waiting
for the break, a close beyond the head invalidates; during the
retracement any high above the head (bearish) / low below the head
(bullish) invalidates. Expiries: 50 bars after the head centre
waiting for the break, 30 bars after the break waiting for the
shoulder, 20 bars after the shoulder is armed waiting for entry.

Columns:
    swing_high / swing_low -- confirmed swing levels, forward-filled
    qm_state -- 0 none, 1 head formed, 2 break confirmed,
                3 shoulder armed (max over the two sides)
    qm_side  -- +1 bearish setup furthest along, -1 bullish, 0 none
    qm_level -- shoulder trigger level RL / RH while a shoulder is
                armed, NaN otherwise
    short_trigger / long_trigger -- True only on the entry bar
    last_bear_head_high / last_bull_head_low -- most recent head
        level, forward-filled (invalidation level for the exit rule)
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT = 2
BREAK_EXPIRY = 50  # bars after the head centre, waiting for the break
RETRACE_EXPIRY = 30  # bars after the break, waiting for the shoulder
SHOULDER_EXPIRY = 20  # bars after the shoulder confirms, waiting for entry

INDICATOR_COLS = ["swing_high", "swing_low", "qm_state", "qm_level", "atr"]

_STAGE_CODE = {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 3}


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)

    swing_high = np.full(n, np.nan)
    swing_low = np.full(n, np.nan)
    qm_state = np.zeros(n, dtype=int)
    qm_side = np.zeros(n, dtype=int)
    qm_level = np.full(n, np.nan)
    short_trig = np.zeros(n, dtype=bool)
    long_trig = np.zeros(n, dtype=bool)
    last_bear_head = np.full(n, np.nan)
    last_bull_head = np.full(n, np.nan)

    last_sh = np.nan
    last_sl = np.nan

    # Bearish state.
    b_stage = 0
    b_H1 = np.nan
    b_L1 = np.nan
    b_H2 = np.nan
    b_H2_idx = -1
    b_break_idx = -1
    b_break_low = np.nan
    b_retrace_high = np.nan
    b_RL = np.nan
    b_RL_conf = -1
    cur_bear_head = np.nan
    # Bullish state (mirror).
    u_stage = 0
    u_L1 = np.nan
    u_H1 = np.nan
    u_L2 = np.nan
    u_L2_idx = -1
    u_break_idx = -1
    u_break_high = np.nan
    u_retrace_low = np.nan
    u_RH = np.nan
    u_RH_conf = -1
    cur_bull_head = np.nan

    cur_qm_level = np.nan

    for i in range(n):
        # ---- pivot confirmation for centre j = i-2 ----
        new_sh = None
        new_sl = None
        j = i - PIVOT
        if j >= PIVOT:
            if h[j] == h[j - PIVOT:j + PIVOT + 1].max() and h[j] > h[j - 1]:
                new_sh = (float(h[j]), j)
            if l[j] == l[j - PIVOT:j + PIVOT + 1].min() and l[j] < l[j - 1]:
                new_sl = (float(l[j]), j)
        if new_sh is not None:
            last_sh = new_sh[0]
        if new_sl is not None:
            last_sl = new_sl[0]

        # ---- bearish machine ----
        if b_stage == 5:
            if c[i] < b_RL:
                short_trig[i] = True
                b_stage = 0
                b_RL = np.nan
            elif h[i] > b_H2 or i - b_RL_conf > SHOULDER_EXPIRY:
                b_stage = 0
                b_RL = np.nan
        elif b_stage == 4:
            b_retrace_high = max(b_retrace_high, h[i])
            b_break_low = min(b_break_low, l[i])
            if h[i] > b_H2 or i - b_break_idx > RETRACE_EXPIRY:
                b_stage = 0
            elif (new_sl is not None and new_sl[1] > b_break_idx
                    and new_sl[0] > b_break_low and b_retrace_high > b_L1):
                b_RL, b_RL_conf = new_sl[0], i
                b_stage = 5
                cur_qm_level = b_RL
        elif b_stage == 3:
            if c[i] < b_L1:
                b_stage = 4
                b_break_idx = i
                b_break_low = l[i]
                b_retrace_high = h[i]
            elif c[i] > b_H2:
                b_stage = 0
            elif new_sh is not None and new_sh[0] > b_H2:
                b_H2, b_H2_idx = new_sh
                cur_bear_head = b_H2
            elif i - b_H2_idx > BREAK_EXPIRY:
                b_stage = 0
        elif b_stage == 2:
            if new_sh is not None and new_sh[0] > b_H1:
                b_H2, b_H2_idx = new_sh
                b_stage = 3
                cur_bear_head = b_H2
            elif new_sl is not None and new_sl[0] < b_L1:
                b_L1 = new_sl[0]
        elif b_stage == 1:
            if new_sl is not None:
                b_L1 = new_sl[0]
                b_stage = 2
            elif new_sh is not None:
                b_H1 = new_sh[0]
        else:
            if new_sh is not None:
                b_H1 = new_sh[0]
                b_stage = 1

        # ---- bullish machine (mirror) ----
        if u_stage == 5:
            if c[i] > u_RH:
                long_trig[i] = True
                u_stage = 0
                u_RH = np.nan
            elif l[i] < u_L2 or i - u_RH_conf > SHOULDER_EXPIRY:
                u_stage = 0
                u_RH = np.nan
        elif u_stage == 4:
            u_retrace_low = min(u_retrace_low, l[i])
            u_break_high = max(u_break_high, h[i])
            if l[i] < u_L2 or i - u_break_idx > RETRACE_EXPIRY:
                u_stage = 0
            elif (new_sh is not None and new_sh[1] > u_break_idx
                    and new_sh[0] < u_break_high and u_retrace_low < u_H1):
                u_RH, u_RH_conf = new_sh[0], i
                u_stage = 5
                cur_qm_level = u_RH
        elif u_stage == 3:
            if c[i] > u_H1:
                u_stage = 4
                u_break_idx = i
                u_break_high = h[i]
                u_retrace_low = l[i]
            elif c[i] < u_L2:
                u_stage = 0
            elif new_sl is not None and new_sl[0] < u_L2:
                u_L2, u_L2_idx = new_sl
                cur_bull_head = u_L2
            elif i - u_L2_idx > BREAK_EXPIRY:
                u_stage = 0
        elif u_stage == 2:
            if new_sl is not None and new_sl[0] < u_L1:
                u_L2, u_L2_idx = new_sl
                u_stage = 3
                cur_bull_head = u_L2
            elif new_sh is not None and new_sh[0] > u_H1:
                u_H1 = new_sh[0]
        elif u_stage == 1:
            if new_sh is not None:
                u_H1 = new_sh[0]
                u_stage = 2
            elif new_sl is not None:
                u_L1 = new_sl[0]
        else:
            if new_sl is not None:
                u_L1 = new_sl[0]
                u_stage = 1

        # ---- record this bar ----
        swing_high[i] = last_sh
        swing_low[i] = last_sl
        b_code = _STAGE_CODE[b_stage]
        u_code = _STAGE_CODE[u_stage]
        qm_state[i] = max(b_code, u_code)
        if b_code > u_code:
            qm_side[i] = 1
        elif u_code > b_code:
            qm_side[i] = -1
        else:
            qm_side[i] = 0
        qm_level[i] = cur_qm_level if (b_stage == 5 or u_stage == 5) else np.nan
        if b_stage != 5 and u_stage != 5:
            cur_qm_level = np.nan
        last_bear_head[i] = cur_bear_head
        last_bull_head[i] = cur_bull_head

    df["swing_high"] = swing_high
    df["swing_low"] = swing_low
    df["qm_state"] = qm_state
    df["qm_side"] = qm_side
    df["qm_level"] = qm_level
    df["short_trigger"] = short_trig
    df["long_trigger"] = long_trig
    df["last_bear_head_high"] = last_bear_head
    df["last_bull_head_low"] = last_bull_head
    return df
