"""Breakout-retest signal engine (polarity principle).

A breakout prints a level; the level is then valid for a 20-bar
retest window. A *clean* retest enters; a *lost* level cancels.

Long side
----------
At breakout bar i (breakout_up): level = level_high[i-1].

For each j in (i, i+20], in order, on bar j's close:
  1. LEVEL LOST (cancel): c[j] < level - 0.5*ATR[j]  -> setup dead,
     no entry will ever fire for it.
  2. EXPIRED (cancel): j > i + 20 -> no signal.
  3. CLEAN RETEST (entry): l[j] <= level + 0.1*ATR[j] (the wick
     touched the zone from above) AND c[j] > level (the close
     rejected back above the line) -> long_entry.

Short side mirrors with level = level_low[i-1]: failure is a
close above level + 0.5*ATR; touch is h[j] >= level - 0.1*ATR[j]
with c[j] < level (closed back below).

Exits: a live position keeps its entry's level as anchor;
long_exit fires when a close loses the line (c[j] < level -
0.5*ATR[j]); short_exit mirrors (c[j] > level + 0.5*ATR[j]).
Only one pending setup per side is tracked — a newer breakout
replaces the old one ("keep only the most recent breakout
setup").

Fixed a priori: 20-bar range, 20-bar retest window, 0.1/0.5 ATR
touch/loss bands. No optimization. Signal on bar j uses only
data through bar j's close; the harness executes at the next
bar's open. Columns are boolean with no NaN.
"""

import numpy as np
import pandas as pd

WINDOW_BARS = 20       # retest window after a breakout (fixed a priori)
TOUCH_ATR_MULT = 0.1   # touch band above/below the level (fixed a priori)
LOSS_ATR_MULT = 0.5    # level-loss band that cancels the setup (fixed a priori)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy()
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    atr_v = df["atr"].to_numpy()
    lvl_hi = df["level_high"].to_numpy()
    lvl_lo = df["level_low"].to_numpy()
    brk_up = df["breakout_up"].fillna(False).to_numpy(dtype=bool)
    brk_dn = df["breakout_dn"].fillna(False).to_numpy(dtype=bool)

    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)

    pend_long = None    # (level, start_bar) of the pending long setup
    pend_short = None   # (level, start_bar) of the pending short setup
    act_long = None     # anchor level of the open long position
    act_short = None    # anchor level of the open short position

    for j in range(n):
        a = atr_v[j]
        cj = c[j]

        # --- resolve pending setups on this bar's close ---
        if pend_long is not None:
            level, start = pend_long
            if j - start > WINDOW_BARS:
                pend_long = None                      # expired
            elif cj < level - LOSS_ATR_MULT * a:
                pend_long = None                      # level lost -> failed retest
            elif l[j] <= level + TOUCH_ATR_MULT * a and cj > level:
                long_entry[j] = True                  # clean retest, rejected up
                act_long = level                      # anchor the position level
                pend_long = None

        if pend_short is not None:
            level, start = pend_short
            if j - start > WINDOW_BARS:
                pend_short = None                     # expired
            elif cj > level + LOSS_ATR_MULT * a:
                pend_short = None                     # level lost -> failed retest
            elif h[j] >= level - TOUCH_ATR_MULT * a and cj < level:
                short_entry[j] = True                 # clean retest, rejected down
                act_short = level
                pend_short = None

        # --- position-level exits (level lost after entry) ---
        if act_long is not None and cj < act_long - LOSS_ATR_MULT * a:
            long_exit[j] = True
            act_long = None
        if act_short is not None and cj > act_short + LOSS_ATR_MULT * a:
            short_exit[j] = True
            act_short = None

        # --- new breakouts arm (or replace) the pending setup ---
        if brk_up[j] and j > 0:
            pend_long = (lvl_hi[j - 1], j)   # most recent wins
        if brk_dn[j] and j > 0:
            pend_short = (lvl_lo[j - 1], j)

    df["long_entry"] = pd.Series(long_entry, index=df.index).astype(bool)
    df["short_entry"] = pd.Series(short_entry, index=df.index).astype(bool)
    df["long_exit"] = pd.Series(long_exit, index=df.index).astype(bool)
    df["short_exit"] = pd.Series(short_exit, index=df.index).astype(bool)
    return df
