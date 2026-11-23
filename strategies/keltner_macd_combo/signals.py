"""Keltner Channel + MACD combo signals.

LONG on a close breaking above the upper Keltner band (transition
only) while the MACD histogram is positive; SHORT on the mirror
break below the lower band while the histogram is negative. The
harness executes at the next bar's open.

Exits (state machine, one pass):
- Long: close back inside the channel (close < upper band) OR
  the MACD histogram turning negative (hist < 0).
- Short: close back inside the channel (close > lower band) OR
  the histogram turning positive (hist > 0).
- Opposite setup while in a position flips it (exit + entry on
  the same bar): a short breakout bar is by construction also a
  close back inside the channel for a long, so the flip is the
  natural consequence of the exit rule, made explicit here.

Transition-only entries: a setup bar while already holding the
same side does not re-enter. All conditions read bar-i values at
bar i; signal columns are boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    kc_upper = df["kc_upper"].to_numpy(dtype=float)
    kc_lower = df["kc_lower"].to_numpy(dtype=float)
    hist = df["macd_hist"].to_numpy(dtype=float)
    long_setup = df["long_setup"].fillna(False).to_numpy(dtype=bool)
    short_setup = df["short_setup"].fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short"
    for i in range(n):
        if pos == "long":
            # NaN comparisons are False, so an exit cannot fire on
            # an unseeded bar.
            if c[i] < kc_upper[i] or hist[i] < 0:
                lx[i] = True
                pos = None
                if short_setup[i]:
                    se[i] = True
                    pos = "short"
        elif pos == "short":
            if c[i] > kc_lower[i] or hist[i] > 0:
                sx[i] = True
                pos = None
                if long_setup[i]:
                    le[i] = True
                    pos = "long"
        if pos is None:
            if long_setup[i]:
                le[i] = True
                pos = "long"
            elif short_setup[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
