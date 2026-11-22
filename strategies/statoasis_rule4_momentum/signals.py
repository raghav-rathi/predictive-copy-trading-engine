"""StatOasis Rule 4 signals: multi-indicator momentum, verbatim.

LONG (source, SPY daily Rule 4, adapted 1d -> 1h):
    RSI(14) > 55 AND Stochastic %K(14, smooth 3) > 50
    AND Williams %R(14) > -50 AND 120h return > 1%,
    fixed 10-bar time exit (no indicator exit).

SHORT is a builder-added mirror of the long-only source:
    RSI(14) < 45 AND %K < 50 AND %R < -50 AND 120h return < -1%,
    fixed 10-bar time exit.

State machine: entries only when flat; on entry the entry bar
is recorded and the exit fires when i - entry_bar >= 10. The
harness executes the entry signal at the next bar's open, so an
exit signal 10 bars after the entry signal means 10 bars held;
risk.max_hold_bars=10 enforces the same bound in the harness.
All conditions read bars <= i; no lookahead.
"""

import numpy as np
import pandas as pd

HOLD_BARS = 10
RET_MIN = 0.01


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    rsi = df["rsi"].to_numpy(dtype=float)
    k = df["stoch_k"].to_numpy(dtype=float)
    wr = df["willr"].to_numpy(dtype=float)
    ret = df["ret_120h"].to_numpy(dtype=float)

    long_cond = (rsi > 55) & (k > 50) & (wr > -50) & (ret > RET_MIN)
    short_cond = (rsi < 45) & (k < 50) & (wr < -50) & (ret < -RET_MIN)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" | "short" | None
    entry_bar = -1
    for i in range(n):
        if pos is not None and i - entry_bar >= HOLD_BARS:
            if pos == "long":
                lx[i] = True
            else:
                sx[i] = True
            pos = None
            entry_bar = -1
        if pos is None:
            if long_cond[i]:
                le[i] = True
                pos = "long"
                entry_bar = i
            elif short_cond[i]:
                se[i] = True
                pos = "short"
                entry_bar = i

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
