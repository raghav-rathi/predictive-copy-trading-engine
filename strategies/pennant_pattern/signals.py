"""Pennant breakout signals.

Entry: while a pennant is armed, a close beyond the frozen range
(high for bull, low for bear) with volume > 1.2x the prior 20-bar
average volume. The harness executes at the next bar's open.

Exit: the opposite direction's volume-confirmed breakout, or the
168-bar max hold in the risk config — nothing else. A failed
breakout (close back inside the range) is left to the 2xATR stop /
2.5xATR trail. Boolean columns, no NaN, no lookahead: the volume
average excludes the current bar, and every condition reads bars
<= i.
"""

import numpy as np
import pandas as pd

VOL_MULT = 1.2


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    d = df["pennant_dir"].fillna(0).to_numpy(dtype=int)
    level = df["pennant_level"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)
    avg = df["vol_avg20"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short"
    for i in range(n):
        di = int(d[i])
        li = level[i]
        vol_ok = np.isfinite(avg[i]) and v[i] > VOL_MULT * avg[i]
        bull_break = di == 1 and np.isfinite(li) and vol_ok and c[i] > li
        bear_break = di == -1 and np.isfinite(li) and vol_ok and c[i] < li
        if pos == "long" and bear_break:
            lx[i] = True
            pos = None
        elif pos == "short" and bull_break:
            sx[i] = True
            pos = None
        if pos is None:
            if bull_break:
                le[i] = True
                pos = "long"
            elif bear_break:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
