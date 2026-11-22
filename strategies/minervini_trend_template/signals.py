"""Minervini Trend Template signals.

Enter only when the full SEPA gate holds AND price breaks out of
its tight base: long on a close above the trailing 20-bar high
while gate_long holds; short on a close below the trailing 20-bar
low while gate_short holds. The harness executes at the next
bar's open, so the entry lands just after the breakout bar closes.

Exits (state machine, one pass):
- 50-SMA violation: long exits on a close below SMA(50), short
  on a close above SMA(50) — Minervini's trend-ride exit.
- Opposite breakout: a short-gate breakdown while long (or a
  long-gate breakout while short) flips the position on the same
  bar (exit + opposite entry).

All conditions read bar-i closes at bar i; signal columns are
boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    sma50 = df["sma50"].to_numpy(dtype=float)
    dh = df["donch_high20"].to_numpy(dtype=float)
    dl = df["donch_low20"].to_numpy(dtype=float)
    gl = df["gate_long"].fillna(False).to_numpy(dtype=bool)
    gs = df["gate_short"].fillna(False).to_numpy(dtype=bool)

    long_trig = gl & (c > dh)
    short_trig = gs & (c < dl)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" | "short" | None
    for i in range(n):
        if pos == "long":
            if c[i] < sma50[i]:
                lx[i] = True
                pos = None
            elif short_trig[i]:
                lx[i] = True
                se[i] = True
                pos = "short"
        elif pos == "short":
            if c[i] > sma50[i]:
                sx[i] = True
                pos = None
            elif long_trig[i]:
                sx[i] = True
                le[i] = True
                pos = "long"
        if pos is None:
            if long_trig[i]:
                le[i] = True
                pos = "long"
            elif short_trig[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
