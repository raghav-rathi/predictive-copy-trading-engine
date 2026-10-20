"""Hikkake confirmation signals.

A trap bar (bull_trap / bear_trap) opens a 3-bar confirmation window:

  long_entry : close above the inside bar's high (trap_high) on bar j,
      where j is the trap bar or one of the next 2 bars.
  short_entry: close below the inside bar's low (trap_low) on bar j,
      where j is the trap bar or one of the next 2 bars.

The trap bar's own close can confirm (classic hikkake: the false-move
bar often snaps back the same bar). Each trap is consumed on first
confirmation; unconfirmed traps expire after CONFIRM_BARS bars.

Exits: the harness stop (1.5xATR), target (3.0xATR) and 20-bar max hold
do the trade management; structurally, an opposite-direction
confirmation closes the position (long_exit = short_entry and
short_exit = long_entry), same convention as the other pattern
strategies in this package.

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import numpy as np
import pandas as pd

from strategies.hikkake import indicators as I


def _confirm(df: pd.DataFrame, trap_col: str, level_col: str,
             bullish: bool) -> np.ndarray:
    """Return boolean entry array: first in-window confirmation per trap."""
    trap = df[trap_col].to_numpy(dtype=bool)
    level = df[level_col].to_numpy(dtype=float)
    close = df["c"].to_numpy(dtype=float)
    n = len(df)
    entry = np.zeros(n, dtype=bool)
    pending: list[tuple[int, float]] = []  # (trap_bar, level)
    for j in range(n):
        # drop expired traps (window is trap bar + CONFIRM_BARS - 1)
        pending = [(ti, lv) for (ti, lv) in pending
                   if j - ti < I.CONFIRM_BARS]
        if trap[j] and np.isfinite(level[j]):
            pending.append((j, level[j]))
        for ti, lv in pending:
            if bullish and close[j] > lv:
                entry[j] = True
                break
            if not bullish and close[j] < lv:
                entry[j] = True
                break
        if entry[j]:
            pending = []  # trap consumed: one entry per pattern
    return entry


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry = _confirm(df, "bull_trap", "trap_high", bullish=True)
    short_entry = _confirm(df, "bear_trap", "trap_low", bullish=False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    # opposite-direction confirmation is a structural exit
    df["long_exit"] = df["short_entry"].astype(bool)
    df["short_exit"] = df["long_entry"].astype(bool)
    return df
