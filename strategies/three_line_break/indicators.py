"""Three-line break indicators.

A three-line break chart draws a new "line" only when price reverses
hard enough to break the range of the last 3 lines:
  * new white (up) line when the close exceeds the high of the last
    3 lines while the developing line is black (down);
  * new black (down) line when the close falls below the low of the
    last 3 lines while the developing line is white;
  * otherwise the close is absorbed into the developing line (its
    high/low extend).

Reference-line convention (documented choice): the "last 3 lines" are
the 2 most recent completed lines plus the developing line. This is the
common programmatic formulation (the developing line is a line on the
chart) and keeps reversals responsive; a 3-completed-line variant is
checked in CALIBRATION.md via n_lines. The first n_lines-1 bars are
seeded as one line per bar so the reversal check has reference lines
from the start (a monotonic run would otherwise be a single
never-completing line).

Columns:
  tlb_dir -- +1 (white/up developing line) / -1 (black/down), per bar
  tlb_run -- bars since the last direction flip (trend length in bars)

No lookahead: the line state on bar i uses closes through i only. The
first two bars seed lines 1 and 2; before 2 completed lines exist no
reversal can trigger, so the direction carries.
"""

import numpy as np
import pandas as pd

from strategies import base as B

N_LINES = 3


def _build_tlb(closes: np.ndarray, n_lines: int = N_LINES) -> tuple:
    """Single numpy loop over closes. Returns (tlb_dir, tlb_run)."""
    n = len(closes)
    tlb_dir = np.full(n, np.nan)
    tlb_run = np.full(n, np.nan)
    if n < 2:
        return tlb_dir, tlb_run

    def _line(a: float, b: float) -> tuple:
        return (max(a, b), min(a, b), 1 if b >= a else -1)

    lines: list[tuple[float, float, int]] = []  # completed (hi, lo, dir)
    # Phase 1: seed one line per bar for the first n_lines-1 bars.
    j = 1
    while j < n and len(lines) < n_lines - 1:
        hi, lo, d = _line(closes[j - 1], closes[j])
        lines.append((hi, lo, d))
        tlb_dir[j - 1] = d
        tlb_run[j - 1] = 1.0
        j += 1
    # Phase 2: the developing line starts where the last seeded line ended.
    cur_hi = cur_lo = closes[j - 1]
    d = lines[-1][2]
    tlb_dir[j - 1] = d
    tlb_run[j - 1] = 1.0
    run = 1
    for i in range(j, n):
        ci = closes[i]
        prev_close = closes[i - 1]
        flipped = False
        if len(lines) >= n_lines - 1:
            ref = lines[-(n_lines - 1):] + [(cur_hi, cur_lo, d)]
            if d == -1 and ci > max(r[0] for r in ref):
                # bullish turnaround: new white line
                lines.append((cur_hi, cur_lo, d))
                cur_hi, cur_lo = max(ci, prev_close), min(ci, prev_close)
                d, flipped, run = 1, True, 1
            elif d == 1 and ci < min(r[1] for r in ref):
                # bearish turnaround: new black line
                lines.append((cur_hi, cur_lo, d))
                cur_hi, cur_lo = max(ci, prev_close), min(ci, prev_close)
                d, flipped, run = -1, True, 1
        if not flipped:
            cur_hi = max(cur_hi, ci)
            cur_lo = min(cur_lo, ci)
            run += 1
        tlb_dir[i] = d
        tlb_run[i] = run
    return tlb_dir, tlb_run


def add_indicators(df: pd.DataFrame, n_lines: int = N_LINES) -> pd.DataFrame:
    df = df.copy()
    closes = df["c"].to_numpy(dtype=float)
    tlb_dir, tlb_run = _build_tlb(closes, n_lines=n_lines)
    df["tlb_dir"] = pd.Series(tlb_dir).ffill().fillna(1.0)
    df["tlb_run"] = pd.Series(tlb_run).ffill().fillna(1.0)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
