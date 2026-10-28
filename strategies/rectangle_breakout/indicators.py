"""Rectangle consolidation indicators (causal).

For each bar i, the rectangle is the range of the PRIOR 20 bars
(bars i-20..i-1): range high = max high, range low = min low.
A bar only ever reads bars before itself, so no lookahead is
possible by construction.

Columns:
    rect_high      -- max high of the prior 20 bars
    rect_low       -- min low of the prior 20 bars
    rect_width_pct -- (rect_high - rect_low) / midpoint
    rect_tight     -- rect_width_pct < 4%
    rect_hold_bars -- consecutive prior bars whose own trailing
                      20-bar window was also tight (the range has
                      "held" this long)
    vol_avg20      -- mean volume of the prior 20 bars
    vol_ratio      -- bar volume / vol_avg20
    atr            -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

WINDOW = 20
MAX_WIDTH = 0.04
MIN_HOLD = 15
VOL_MULT = 1.2


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)

    rh = df["h"].rolling(WINDOW, min_periods=WINDOW).max().shift(1)
    rl = df["l"].rolling(WINDOW, min_periods=WINDOW).min().shift(1)
    mid = (rh + rl) / 2
    width = (rh - rl) / mid

    # trailing-window width ending at each bar (for the hold count):
    # w[k] is the width of the 20-bar window ending at bar k.
    w_end = (
        (df["h"].rolling(WINDOW, min_periods=WINDOW).max()
         - df["l"].rolling(WINDOW, min_periods=WINDOW).min())
        / ((df["h"].rolling(WINDOW, min_periods=WINDOW).max()
            + df["l"].rolling(WINDOW, min_periods=WINDOW).min()) / 2)
    )
    tight_end = (w_end < MAX_WIDTH).fillna(False).to_numpy(dtype=bool)

    # hold[i] = consecutive tight windows ending at bars i-1, i-2, ...
    hold = np.zeros(n, dtype=int)
    run = 0
    for i in range(n):
        # run counts tight windows ending at or before i-1
        if i >= 1:
            run = run + 1 if tight_end[i - 1] else 0
        hold[i] = run

    vol_avg = df["v"].rolling(WINDOW, min_periods=WINDOW).mean().shift(1)
    vol_ratio = df["v"] / vol_avg

    df["rect_high"] = rh
    df["rect_low"] = rl
    df["rect_width_pct"] = width
    df["rect_tight"] = (width < MAX_WIDTH).fillna(False)
    df["rect_hold_bars"] = hold
    df["vol_avg20"] = vol_avg
    df["vol_ratio"] = vol_ratio
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
