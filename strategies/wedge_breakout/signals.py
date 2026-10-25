"""Wedge breakout signals.

Same state machine as the other pattern strategies: level-based
entries on the trendline break, exits on a close back inside the
entry level or the opposite wedge's breakout. Note the entry level is
the extrapolated trendline value on the entry bar, frozen in the
position record — the line keeps moving after entry, but the exit
level does not. Boolean columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    d = df["wedge_dir"].to_numpy(dtype=int)
    level = df["wedge_level"].to_numpy(dtype=float)
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
            if di == -1 and ci < li:
                se[i] = True
                pos = {"side": "short", "level": li}
            elif di == 1 and ci > li:
                le[i] = True
                pos = {"side": "long", "level": li}

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
