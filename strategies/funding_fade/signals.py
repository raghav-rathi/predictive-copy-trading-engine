"""Negative-funding fade signals.

LONG ONLY (the source thesis is long-only: negative funding means
shorts are paying longs, i.e. crowded-short sentiment to fade).
No short entries are ever emitted.

Enter long on the funding-neg-turn bar (funding_rate < 0 after a bar
>= 0); the harness executes at the next bar's open. Hold exactly 8
bars: long_exit fires 8 bars after the entry signal bar, so the
harness exits at the open 8 bars after the entry bar — the 8h hold
Jlabs found best (Sharpe 0.84, +227.67% since 2020, max drawdown
-14.77%, only 14% time in market). The harness max_hold_bars=8 is
the backstop for the same exit.

The state machine tracks the entry signal bar so the 8-bar count
survives bars where funding flips back positive mid-hold: the exit
is time-based, not funding-based. A new turn-negative signal while
already holding is ignored (one position at a time).

All conditions read bar-j closes/funding at bar j; the harness
executes at the next bar's open. Signal columns are boolean, no
NaN, no lookahead.
"""

import numpy as np
import pandas as pd

HOLD_BARS = 8  # Jlabs 8h hold


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    turn = df["funding_neg_turn"].fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    entry_bar = None  # signal bar of the open long
    for i in range(n):
        if entry_bar is not None and i - entry_bar >= HOLD_BARS:
            lx[i] = True
            entry_bar = None
        if entry_bar is None and turn[i]:
            le[i] = True
            entry_bar = i

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
