"""Ross Hook continuation indicators (Joe Ross 1-2-3 + Hook).

A Ross Hook is the continuation leg of a 1-2-3 formation: after the
1-2-3 completes and price breaks out past point 2, the first small
corrective "hook" that holds above point 3 is the entry trigger.

Detection here is pivot-based (a faithful, fully mechanical
simplification of Ross's discretionary chart pattern):

  N=5-bar fractal pivots: a pivot high at bar i-2 is confirmed when
      h[i-2] == max(h[i-4..i]) with strict inequality against the two
      adjacent bars (ties broken by keeping the first). Pivots are
      stored *shifted by 2* so the pivot column at bar j describes a
      pivot whose center is bar j-2 -- i.e. fully known at bar j's
      close, no lookahead.

Columns:
  piv_high      -- bool: confirmed 5-bar pivot high (centered at j-2)
  piv_low       -- bool: confirmed 5-bar pivot low (centered at j-2)
  piv_high_px   -- high price at a piv_high bar, NaN otherwise
  piv_low_px    -- low price at a piv_low bar, NaN otherwise
  atr           -- ATR(14) for risk scaling
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT_N = 5  # fractal window (bars on each side = (N-1)/2 = 2)
PIVOT_SIDE = 2


def _fractals(values: np.ndarray, kind: str, side: int) -> np.ndarray:
    """Confirmed-at-close fractal pivot flags, centered index -> shifted.

    ``side`` bars on each side of the center (window = 2*side+1). Returns
    a boolean array aligned so that flag[j] is True when bar j-side is
    a fractal pivot (the full window was known at bar j's close). This
    preserves the no-lookahead contract: nothing about bars > j-side
    leaks into the flag at j.
    """
    n = len(values)
    center_flag = np.zeros(n, dtype=bool)
    for i in range(side, n - side):
        win = values[i - side: i + side + 1]
        # strict vs the window EDGES (adjacent ties allowed; the dedupe
        # below keeps the first of a tied run)
        if kind == "high":
            if values[i] == win.max() and values[i] > values[i - side] \
                    and values[i] > values[i + side]:
                center_flag[i] = True
        else:
            if values[i] == win.min() and values[i] < values[i - side] \
                    and values[i] < values[i + side]:
                center_flag[i] = True
    # consecutive ties: keep only the first of a run of equal extremes
    out = np.zeros(n, dtype=bool)
    prev = -10
    for i in range(n):
        if center_flag[i] and i - prev > side:
            out[i + side] = True  # confirmed at bar i+side's close
            prev = i
    return out


def add_indicators(df: pd.DataFrame, pivot_n: int = PIVOT_N) -> pd.DataFrame:
    side = max(1, (pivot_n - 1) // 2)
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    piv_high = _fractals(h, "high", side)
    piv_low = _fractals(l, "low", side)
    df["piv_high"] = piv_high
    df["piv_low"] = piv_low
    # pivot prices are the CENTER bar's extreme (flag at j -> center j-side)
    df["piv_high_px"] = np.where(piv_high, pd.Series(h).shift(side).to_numpy(), np.nan)
    df["piv_low_px"] = np.where(piv_low, pd.Series(l).shift(side).to_numpy(), np.nan)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
