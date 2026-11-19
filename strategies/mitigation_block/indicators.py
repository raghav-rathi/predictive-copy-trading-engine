"""ICT mitigation block indicators.

Causal 5-bar pivots (recorded at the confirmation bar centre+2,
as in quasimodo). Bearish mitigation block: price makes a swing
high H1, pulls back to a swing low L1, rallies to a LOWER high H2
(the failure swing — H2 < H1; the prior high is never traded
through), then closes below L1 (structure break). The last up-close
candle at L1 — the pivot-confirmation bar's candle, i.e. the bar
at the L1 centre — becomes the mitigation block, zone [low, high]
of that candle. Short on the first return into the block (close
inside the block range) after the break; exit on a close above the
block high. Bullish mirror: swing low L1, bounce to swing high H1,
drop to a HIGHER low L2 (never trades through L1), close above H1;
block = the last down-close candle at H1 (the bar at the H1
centre); long on the return into it; exit on a close below the
block low. Blocks expire 150 bars after the break; only the most
recent block per side is active (a newer break replaces an armed
block).

This is distinct from breaker_block (which requires a SWEEP of the
prior extreme first — price trading through it before the block
flips) and from order_block_retest (a fresh block, no failure
swing): here the defining feature is the failure swing that never
reaches the prior extreme, then the structure break.

Columns:
    swing_high / swing_low -- confirmed swing levels, forward-filled
    bear_block_bottom / bear_block_top -- armed bearish block zone,
        NaN when none is armed
    bull_block_bottom / bull_block_top -- armed bullish block zone
    mb_state -- 0 none, 1 a setup is forming, 2 a block is armed
    mb_side -- +1 the bearish side is furthest along, -1 bullish,
        0 none / tied
    long_trigger / short_trigger -- True only on the entry bar
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT = 2
BLOCK_EXPIRY_BARS = 150  # bars after the break, waiting for the return

INDICATOR_COLS = ["swing_high", "swing_low", "bear_block_bottom",
                  "bear_block_top", "bull_block_bottom",
                  "bull_block_top", "mb_state", "mb_side", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)

    swing_high = np.full(n, np.nan)
    swing_low = np.full(n, np.nan)
    bear_bot = np.full(n, np.nan)
    bear_top = np.full(n, np.nan)
    bull_bot = np.full(n, np.nan)
    bull_top = np.full(n, np.nan)
    mb_state = np.zeros(n, dtype=int)
    mb_side = np.zeros(n, dtype=int)
    long_trig = np.zeros(n, dtype=bool)
    short_trig = np.zeros(n, dtype=bool)

    last_sh = np.nan
    last_sl = np.nan

    # Bearish setup: stage 1 H1, 2 L1, 3 H2 (failure swing).
    b_stage = 0
    b_H1 = np.nan
    b_L1 = np.nan
    b_L1_idx = -1
    b_H2 = np.nan
    # Bullish setup (mirror): stage 1 L1, 2 H1, 3 L2.
    u_stage = 0
    u_L1 = np.nan
    u_H1 = np.nan
    u_H1_idx = -1
    u_L2 = np.nan
    # Armed blocks: dict(bottom, top, break_idx, entered) or None.
    bear_block = None
    bull_block = None

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

        # ---- bearish setup machine ----
        # A high through H1 while the failure swing is forming kills
        # the setup (the prior high was traded through).
        if b_stage in (2, 3) and h[i] > b_H1:
            b_stage = 0
            b_H1 = b_L1 = b_H2 = np.nan
            b_L1_idx = -1
        if b_stage == 3:
            if c[i] < b_L1:
                bear_block = {"bottom": float(l[b_L1_idx]),
                              "top": float(h[b_L1_idx]),
                              "break_idx": i, "entered": False}
                b_stage = 0
                b_H1 = b_L1 = b_H2 = np.nan
                b_L1_idx = -1
            elif new_sh is not None and new_sh[0] >= b_H1:
                b_H1 = new_sh[0]
                b_stage = 1
                b_L1 = b_H2 = np.nan
                b_L1_idx = -1
            elif new_sh is not None and new_sh[0] > b_H2:
                b_H2 = new_sh[0]
            elif new_sl is not None and new_sl[0] < b_L1:
                b_L1, b_L1_idx = new_sl
        elif b_stage == 2:
            if new_sh is not None and new_sh[0] >= b_H1:
                b_H1 = new_sh[0]
                b_stage = 1
                b_L1 = b_H2 = np.nan
                b_L1_idx = -1
            elif new_sh is not None:
                b_H2 = new_sh[0]
                b_stage = 3
            elif new_sl is not None and new_sl[0] < b_L1:
                b_L1, b_L1_idx = new_sl
        elif b_stage == 1:
            if new_sl is not None:
                b_L1, b_L1_idx = new_sl
                b_stage = 2
            elif new_sh is not None and new_sh[0] > b_H1:
                b_H1 = new_sh[0]
        else:
            if new_sh is not None:
                b_H1 = new_sh[0]
                b_stage = 1
        # A break/invalidation that reset the machine on this bar
        # must not drop a swing high confirmed on the same bar.
        if b_stage == 0 and new_sh is not None:
            b_H1 = new_sh[0]
            b_stage = 1

        # ---- bullish setup machine (mirror) ----
        if u_stage in (2, 3) and l[i] < u_L1:
            u_stage = 0
            u_L1 = u_H1 = u_L2 = np.nan
            u_H1_idx = -1
        if u_stage == 3:
            if c[i] > u_H1:
                bull_block = {"bottom": float(l[u_H1_idx]),
                              "top": float(h[u_H1_idx]),
                              "break_idx": i, "entered": False}
                u_stage = 0
                u_L1 = u_H1 = u_L2 = np.nan
                u_H1_idx = -1
            elif new_sl is not None and new_sl[0] <= u_L1:
                u_L1 = new_sl[0]
                u_stage = 1
                u_H1 = u_L2 = np.nan
                u_H1_idx = -1
            elif new_sl is not None and new_sl[0] < u_L2:
                u_L2 = new_sl[0]
            elif new_sh is not None and new_sh[0] > u_H1:
                u_H1, u_H1_idx = new_sh
        elif u_stage == 2:
            if new_sl is not None and new_sl[0] <= u_L1:
                u_L1 = new_sl[0]
                u_stage = 1
                u_H1 = u_L2 = np.nan
                u_H1_idx = -1
            elif new_sl is not None:
                u_L2 = new_sl[0]
                u_stage = 3
            elif new_sh is not None and new_sh[0] > u_H1:
                u_H1, u_H1_idx = new_sh
        elif u_stage == 1:
            if new_sh is not None:
                u_H1, u_H1_idx = new_sh
                u_stage = 2
            elif new_sl is not None and new_sl[0] < u_L1:
                u_L1 = new_sl[0]
        else:
            if new_sl is not None:
                u_L1 = new_sl[0]
                u_stage = 1
        if u_stage == 0 and new_sl is not None:
            u_L1 = new_sl[0]
            u_stage = 1

        # ---- armed blocks: expiry, entry, invalidation ----
        if bear_block is not None and i - bear_block["break_idx"] > BLOCK_EXPIRY_BARS:
            bear_block = None
        if bull_block is not None and i - bull_block["break_idx"] > BLOCK_EXPIRY_BARS:
            bull_block = None
        # The block is published for this bar even on the bar its
        # top/bottom is closed through, so the signal layer sees
        # the exit close.
        clear_bear_after = False
        clear_bull_after = False
        if bear_block is not None:
            if c[i] > bear_block["top"]:
                clear_bear_after = True
            elif (not bear_block["entered"]
                    and bear_block["bottom"] <= c[i] <= bear_block["top"]):
                short_trig[i] = True
                bear_block["entered"] = True
        if bull_block is not None:
            if c[i] < bull_block["bottom"]:
                clear_bull_after = True
            elif (not bull_block["entered"]
                    and bull_block["bottom"] <= c[i] <= bull_block["top"]):
                long_trig[i] = True
                bull_block["entered"] = True

        # ---- record this bar ----
        swing_high[i] = last_sh
        swing_low[i] = last_sl
        if bear_block is not None:
            bear_bot[i] = bear_block["bottom"]
            bear_top[i] = bear_block["top"]
        if bull_block is not None:
            bull_bot[i] = bull_block["bottom"]
            bull_top[i] = bull_block["top"]
        bear_score = 4 if bear_block is not None else b_stage
        bull_score = 4 if bull_block is not None else u_stage
        mb_state[i] = 2 if (bear_block is not None or bull_block is not None) else (
            1 if (b_stage >= 1 or u_stage >= 1) else 0)
        if bear_score > bull_score:
            mb_side[i] = 1
        elif bull_score > bear_score:
            mb_side[i] = -1
        else:
            mb_side[i] = 0
        if clear_bear_after:
            bear_block = None
        if clear_bull_after:
            bull_block = None

    df["swing_high"] = swing_high
    df["swing_low"] = swing_low
    df["bear_block_bottom"] = bear_bot
    df["bear_block_top"] = bear_top
    df["bull_block_bottom"] = bull_bot
    df["bull_block_top"] = bull_top
    df["mb_state"] = mb_state
    df["mb_side"] = mb_side
    df["long_trigger"] = long_trig
    df["short_trigger"] = short_trig
    return df
