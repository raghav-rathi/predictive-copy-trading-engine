"""StatOasis Rule 5 signals.

SHORT on the double-overbought fade (RSI(14) > 70 AND Williams
%R(14) > -10 AND SMA(100) falling); LONG on the mirror
(RSI < 30 AND %R < -90 AND SMA(100) rising, builder-added).
The harness executes at the next bar's open.

Exit: a FIXED 5-bar hold, implemented as a bar-count state
machine — the exit signal fires on the 5th bar after the entry
bar, so the position is held ~5h. No signal-level stop or target;
the harness's 2xATR stop and 5-bar max hold are the backstops.
While a position is open, no new entry fires.

All conditions read bar-i values at bar i; signal columns are
boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd

HOLD_BARS = 5


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    short_setup = df["short_setup"].fillna(False).to_numpy(dtype=bool)
    long_setup = df["long_setup"].fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # {"side": "long"/"short", "held": int}
    for i in range(n):
        if pos is not None:
            pos["held"] += 1
            if pos["held"] >= HOLD_BARS:
                if pos["side"] == "long":
                    lx[i] = True
                else:
                    sx[i] = True
                pos = None
        if pos is None:
            if short_setup[i]:
                se[i] = True
                pos = {"side": "short", "held": 0}
            elif long_setup[i]:
                le[i] = True
                pos = {"side": "long", "held": 0}

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
