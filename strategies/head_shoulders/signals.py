"""Head and shoulders neckline-break signals.

Same state machine as double_top_bottom: level-based entries on the
neckline break (the break often precedes the right shoulder's
confirmation), exits on neckline reclaim or the opposite pattern.
Boolean columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    d = df["hs_dir"].to_numpy(dtype=int)
    neck = df["hs_neck"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # {"side": "long"/"short", "neck": float}
    for i in range(n):
        di = int(d[i])
        ni = float(neck[i])
        ci = float(c[i])
        if pos is not None:
            if pos["side"] == "short":
                if ci > pos["neck"] or (di == 1 and np.isfinite(ni) and ci > ni):
                    sx[i] = True
                    pos = None
            else:
                if ci < pos["neck"] or (di == -1 and np.isfinite(ni) and ci < ni):
                    lx[i] = True
                    pos = None
        if pos is None and di != 0 and np.isfinite(ni):
            if di == -1 and ci < ni:
                se[i] = True
                pos = {"side": "short", "neck": ni}
            elif di == 1 and ci > ni:
                le[i] = True
                pos = {"side": "long", "neck": ni}

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
