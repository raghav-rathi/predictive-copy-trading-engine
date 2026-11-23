"""Wilder Parabolic SAR signals.

The SAR flip IS the trade: price is either above the SAR (long
trend) or below it (short trend), so the system is always in the
market once entered — there is no flat state in Wilder's
original. The signal layer adds one flat state only at the very
start:

- Position starts flat. Bar 0 is seeded LONG by the indicator
  layer, but bar 0 emits NO entry (the seed is arbitrary, not a
  signal — see indicators.py). The first entry fires on the
  first genuine flip after bar 0.
- Flip to LONG while flat or short: long_entry (plus
  short_exit if a short was open).
- Flip to SHORT while flat or long: short_entry (plus
  long_exit if a long was open).
- No re-entry while the trend persists: entries are
  transition-only, driven by changes in psar_dir.

The flip bar's signal executes at the next bar's open per the
house convention, so the flip is confirmed on the close before
money goes in. The 2xATR harness stop in risk.py is a backstop
only — the SAR flip is the real exit.

All signal columns are boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    direction = df["psar_dir"].to_numpy(dtype=int)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # None | "long" | "short"; starts flat (bar 0: no entry)
    prev_dir = direction[0] if n else 1
    for i in range(n):
        d = direction[i]
        flipped = (i > 0 and d != prev_dir)
        prev_dir = d
        if not flipped:
            continue
        if d == 1:
            if pos == "short":
                sx[i] = True
                le[i] = True
                pos = "long"
            elif pos is None:
                le[i] = True
                pos = "long"
        else:
            if pos == "long":
                lx[i] = True
                se[i] = True
                pos = "short"
            elif pos is None:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
