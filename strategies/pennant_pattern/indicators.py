"""Classic pennant continuation (Edwards & Magee / StockCharts).

State machine, all causal:

1. Pole: a completed 5-bar move of at least 3x ATR(14). "Completed"
   means the pole's last bar stalled (|close change| <= 0.5x ATR),
   so a steady trend cannot trigger mid-pole. Pole direction is the
   sign of the 5-bar close move.
2. Consolidation: 5-15 bars after the pole bar. Convergence is
   tested from the 5th consolidation bar onward by comparing
   3-bar blocks: the last 3 bars' high-max must be BELOW the
   previous 3 bars' high-max (successive highs falling) and the
   last 3 bars' low-min must be ABOVE the previous 3 bars' low-min
   (successive lows rising). When convergence holds, the setup
   arms and the range freezes at the consolidation's high/low.
3. Armed: the setup stays armed until a volume-confirmed breakout
   (see signals.py), a wrong-side break beyond the far side of the
   range by more than 0.5x ATR (invalidation), or 15 bars pass
   without a breakout (expiry).

Columns:
    pennant_dir  -- +1 while a bull pennant is armed, -1 bear, else 0
    pennant_level -- range high (bull) / range low (bear) while armed
    vol_avg20    -- mean volume over the prior 20 bars (shifted, so
                    the current bar is never in its own average)
    atr          -- Wilder ATR(14)

No lookahead: every decision reads bars <= i. The breakout bar
itself still shows the armed setup (the armed->idle transition on
a confirmed breakout applies from the NEXT bar), so signals.py can
see the breakout bar's level.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_N = 14
POLE_BARS = 5
POLE_MIN_ATR = 3.0
STALL_ATR = 0.5
CONS_MIN_BARS = 5    # consolidation bars (inclusive of the pole bar)
CONS_MAX_BARS = 15
BLOCK = 3            # bars per side in the convergence comparison
FAIL_ATR = 0.5
ARMED_MAX_BARS = 15
VOL_BARS = 20
VOL_MULT = 1.2


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)
    atr = B.atr(df["h"], df["l"], df["c"], ATR_N).to_numpy(dtype=float)
    vol_avg = (
        df["v"].rolling(VOL_BARS, min_periods=VOL_BARS).mean().shift(1)
    ).to_numpy(dtype=float)

    dir_col = np.zeros(n, dtype=int)
    level_col = np.full(n, np.nan)

    state = "idle"  # idle | consolidating | armed
    pole_dir = 0
    cons_start = -1
    cons_high = float("nan")
    cons_low = float("nan")
    armed_bar = -1
    range_high = float("nan")
    range_low = float("nan")

    def _vol_confirmed_breakout(bar: int) -> bool:
        """Was `bar` a volume-confirmed breakout of the frozen range?"""
        if bar < 1 or not np.isfinite(vol_avg[bar]):
            return False
        if v[bar] <= VOL_MULT * vol_avg[bar]:
            return False
        if pole_dir == 1:
            return c[bar] > range_high
        return c[bar] < range_low

    for i in range(n):
        a = atr[i] if np.isfinite(atr[i]) else 0.0
        if state == "idle":
            stalled = i >= 1 and a > 0 and abs(c[i] - c[i - 1]) <= STALL_ATR * a
            if a > 0 and stalled and i >= POLE_BARS:
                up = c[i] - c[i - POLE_BARS]
                dn = c[i - POLE_BARS] - c[i]
                if up >= POLE_MIN_ATR * a:
                    state = "consolidating"
                    pole_dir = 1
                    cons_start = i
                    cons_high = h[i]
                    cons_low = l[i]
                elif dn >= POLE_MIN_ATR * a:
                    state = "consolidating"
                    pole_dir = -1
                    cons_start = i
                    cons_high = h[i]
                    cons_low = l[i]
        elif state == "consolidating":
            cons_high = max(cons_high, h[i])
            cons_low = min(cons_low, l[i])
            length = i - cons_start + 1
            if length > CONS_MAX_BARS:
                state = "idle"
            elif length >= CONS_MIN_BARS and i >= 2 * BLOCK:
                last_h = h[i - BLOCK + 1:i + 1].max()
                prev_h = h[i - 2 * BLOCK + 1:i - BLOCK + 1].max()
                last_l = l[i - BLOCK + 1:i + 1].min()
                prev_l = l[i - 2 * BLOCK + 1:i - BLOCK + 1].min()
                if last_h < prev_h and last_l > prev_l:
                    state = "armed"
                    armed_bar = i
                    range_high = cons_high
                    range_low = cons_low
        elif state == "armed":
            if _vol_confirmed_breakout(i - 1):
                state = "idle"
            elif pole_dir == 1 and c[i] < range_low - FAIL_ATR * a:
                state = "idle"
            elif pole_dir == -1 and c[i] > range_high + FAIL_ATR * a:
                state = "idle"
            elif i - armed_bar > ARMED_MAX_BARS:
                state = "idle"

        if state == "armed":
            dir_col[i] = pole_dir
            level_col[i] = range_high if pole_dir == 1 else range_low
        else:
            dir_col[i] = 0
            level_col[i] = np.nan

    df["pennant_dir"] = dir_col
    df["pennant_level"] = level_col
    df["vol_avg20"] = vol_avg
    df["atr"] = atr
    return df
