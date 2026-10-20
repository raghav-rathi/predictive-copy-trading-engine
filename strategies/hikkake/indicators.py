"""Hikkake pattern (Daniel L. Chesler, CMT, Active Trader Magazine, April 2004).

The Hikkake ("to trick, trap, or ensnare") is a false-breakout pattern
built on an inside bar:

  inside bar (bar i-1): h < h[i-2] AND l > l[i-2]
  bullish setup: bar i prints a LOWER low AND LOWER high than the inside
      bar -> a failed breakdown; trapped shorts cover when price
      confirms back above the inside bar's high.
  bearish setup: bar i prints a HIGHER high AND HIGHER low than the
      inside bar -> a failed breakout; trapped longs dump when price
      confirms back below the inside bar's low.

Confirmation must arrive within 3 bars of the trap bar, or the pattern
expires (Chesler's original rule).

Columns (all computable from bars <= i, no lookahead):
  inside_bar   -- inside-bar flag
  bull_trap    -- failed-breakdown bar (confirmation pending, long side)
  bear_trap    -- failed-breakout bar (confirmation pending, short side)
  trap_high    -- inside bar's high at a bull_trap bar (confirmation level)
  trap_low     -- inside bar's low at a bear_trap bar (confirmation level)
  atr          -- ATR(14) for risk scaling
"""

import numpy as np
import pandas as pd

from strategies import base as B

CONFIRM_BARS = 3  # confirmation window after the trap bar (Chesler)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"]
    l = df["l"]
    h1 = h.shift(1)
    l1 = l.shift(1)

    inside = (h < h1) & (l > l1)
    df["inside_bar"] = inside.fillna(False).astype(bool)

    ib = inside.shift(1).fillna(False).astype(bool)  # inside bar is bar i-1
    bull_trap = ib & (h < h1) & (l < l1)   # failed breakdown
    bear_trap = ib & (h > h1) & (l > l1)   # failed breakout
    df["bull_trap"] = bull_trap.fillna(False).astype(bool)
    df["bear_trap"] = bear_trap.fillna(False).astype(bool)

    # confirmation levels: the inside bar's high/low (bar i-1's range)
    df["trap_high"] = np.where(df["bull_trap"], h1, np.nan)
    df["trap_low"] = np.where(df["bear_trap"], l1, np.nan)

    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
