"""Swing support / resistance bounce signals.

State machine over bars (one position at a time, mirroring the
harness):

    long_entry  -- bar low dips within 0.3% of support, close back
                   above support, close above open (a bounce, not a
                   falling knife catching the level on the way down)
    short_entry -- bar high reaches within 0.3% of resistance, close
                   back below resistance, close below open
    long_exit   -- close 0.5% below the entry support (level failed),
                   or a short bounce fires (opposite signal)
    short_exit  -- close 0.5% above the entry resistance, or a long
                   bounce fires

The entry support/resistance is frozen in the position record: levels
move as new pivots confirm, but the trade's failure level does not.
Boolean columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd

TOUCH_TOL = 0.003  # bar must dip within 0.3% of the level
FAIL_TOL = 0.005   # close 0.5% beyond the level = failure


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    o = df["o"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    sup = df["sr_support"].to_numpy(dtype=float)
    res = df["sr_resistance"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # {"side": "long"/"short", "level": float}
    for i in range(n):
        si = float(sup[i])
        ri = float(res[i])
        ci = float(c[i])
        long_bounce = (
            np.isfinite(si)
            and l[i] <= si * (1.0 + TOUCH_TOL)
            and ci > si
            and ci > o[i]
        )
        short_bounce = (
            np.isfinite(ri)
            and h[i] >= ri * (1.0 - TOUCH_TOL)
            and ci < ri
            and ci < o[i]
        )
        if pos is not None:
            if pos["side"] == "long":
                if ci < pos["level"] * (1.0 - FAIL_TOL) or short_bounce:
                    lx[i] = True
                    pos = None
            else:
                if ci > pos["level"] * (1.0 + FAIL_TOL) or long_bounce:
                    sx[i] = True
                    pos = None
        if pos is None:
            if long_bounce:
                le[i] = True
                pos = {"side": "long", "level": si}
            elif short_bounce:
                se[i] = True
                pos = {"side": "short", "level": ri}

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
