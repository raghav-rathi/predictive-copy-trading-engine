"""Buyable Gap-Up signals.

LONG on a gap-up bar (open >= 0.75xATR(40) above the prior close
on >= 1.5x the 1200-bar average volume, in an uptrend); SHORT on
the mirror gap-down (builder-added). The harness executes at the
next bar's open.

Exits (state machine, one pass — the gap bar's extreme is the
stop, tracked from the entry bar):
- Long: close below the gap bar's intraday low (the gap has
  failed — price gave back the whole gap), OR close below the
  240-bar SMA (the 10-day moving-average violation, simplified:
  the original exits on the 10-day violation only if the stock
  respected the 10-day for >= 7 weeks, else on the 50-day
  violation; we always use the 10-day equivalent).
- Short: close above the gap bar's intraday high, OR close above
  the 240-bar SMA.
- Opposite setup while in a position flips it (exit + entry on
  the same bar, with the new gap bar's extreme tracked).

All conditions read bar-i values at bar i; signal columns are
boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    sma240 = df["sma240"].to_numpy(dtype=float)
    long_setup = df["long_setup"].fillna(False).to_numpy(dtype=bool)
    short_setup = df["short_setup"].fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # {"side": "long"/"short", "level": float}
    for i in range(n):
        if pos is not None:
            if pos["side"] == "long":
                if c[i] < pos["level"] or c[i] < sma240[i]:
                    lx[i] = True
                    pos = None
                elif short_setup[i]:
                    lx[i] = True
                    se[i] = True
                    pos = {"side": "short", "level": h[i]}
            else:
                if c[i] > pos["level"] or c[i] > sma240[i]:
                    sx[i] = True
                    pos = None
                elif long_setup[i]:
                    sx[i] = True
                    le[i] = True
                    pos = {"side": "long", "level": l[i]}
        if pos is None:
            if long_setup[i]:
                le[i] = True
                pos = {"side": "long", "level": l[i]}
            elif short_setup[i]:
                se[i] = True
                pos = {"side": "short", "level": h[i]}

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
