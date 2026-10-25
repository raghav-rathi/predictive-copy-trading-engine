"""Flag breakout signals.

Same state machine as the other pattern strategies: level-based
entries on the consolidation breakout (long above the consolidation
high for bull flags, short below the consolidation low for bear
flags), exits on a close back below/above the entry level (failed
breakout) or the opposite flag's breakout. Boolean columns, no NaN,
no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    d = df["flag_dir"].to_numpy(dtype=int)
    level = df["flag_level"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # {"side": "long"/"short", "level": float}
    for i in range(n):
        di = int(d[i])
        li = float(level[i])
        ci = float(c[i])
        if pos is not None:
            if pos["side"] == "short":
                if ci > pos["level"] or (di == 1 and np.isfinite(li) and ci > li):
                    sx[i] = True
                    pos = None
            else:
                if ci < pos["level"] or (di == -1 and np.isfinite(li) and ci < li):
                    lx[i] = True
                    pos = None
        if pos is None and di != 0 and np.isfinite(li):
            if di == 1 and ci > li:
                le[i] = True
                pos = {"side": "long", "level": li}
            elif di == -1 and ci < li:
                se[i] = True
                pos = {"side": "short", "level": li}

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
