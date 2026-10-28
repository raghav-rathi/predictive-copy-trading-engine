"""Rectangle breakout signals.

    long_entry  -- tight range held >= 15 bars, close above the
                   prior-20-bar range high, volume > 1.2x average
    short_entry -- mirror below the range low
    long_exit   -- close back below the range low, or a short
                   breakout on the same bar
    short_exit  -- close back above the range high, or a long
                   breakout on the same bar

A small state machine keeps one position at a time in signal
space: entries only fire while flat, exits only while in the
matching position. Boolean columns, no NaN, no lookahead (all
inputs are prior-bar ranges or the current bar's close/volume).
"""

import numpy as np
import pandas as pd

from strategies.rectangle_breakout.indicators import MIN_HOLD, VOL_MULT


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    rh = df["rect_high"].to_numpy(dtype=float)
    rl = df["rect_low"].to_numpy(dtype=float)
    tight = df["rect_tight"].to_numpy(dtype=bool)
    hold = df["rect_hold_bars"].to_numpy(dtype=int)
    vr = df["vol_ratio"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" | "short" | None
    for i in range(n):
        brk_long = bool(
            tight[i] and hold[i] >= MIN_HOLD
            and np.isfinite(vr[i]) and vr[i] > VOL_MULT
            and np.isfinite(rh[i]) and c[i] > rh[i]
        )
        brk_short = bool(
            tight[i] and hold[i] >= MIN_HOLD
            and np.isfinite(vr[i]) and vr[i] > VOL_MULT
            and np.isfinite(rl[i]) and c[i] < rl[i]
        )
        if pos == "long":
            if (np.isfinite(rl[i]) and c[i] < rl[i]) or brk_short:
                lx[i] = True
                pos = None
        elif pos == "short":
            if (np.isfinite(rh[i]) and c[i] > rh[i]) or brk_long:
                sx[i] = True
                pos = None
        if pos is None:
            if brk_long:
                le[i] = True
                pos = "long"
            elif brk_short:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
