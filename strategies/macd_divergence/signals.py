"""MACD histogram divergence signals.

    long_entry  -- bullish divergence bar (price lower low, histogram
                   higher low)
    short_entry -- bearish divergence bar (price higher high, histogram
                   lower high)
    long_exit   -- histogram crosses back below zero AFTER having been
                   positive during the position, or a bearish divergence
                   bar (opposite signal)
    short_exit  -- histogram crosses back above zero AFTER having been
                   negative during the position, or a bullish divergence
                   bar

The "seen positive/negative" guard matters: a bullish divergence
usually fires while the histogram is still negative, so a plain
"exit when hist < 0" rule would exit on the very next bar. The
position must first see the histogram confirm (cross zero in the
trade's direction) before a zero cross back counts as an exit.
Boolean columns, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    d = df["macd_div_dir"].to_numpy(dtype=int)
    hist = df["macd_hist"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # {"side": "long"/"short", "seen": bool}
    for i in range(n):
        di = int(d[i])
        hi = float(hist[i])
        if pos is not None:
            if pos["side"] == "long":
                if np.isfinite(hi) and hi > 0:
                    pos["seen"] = True
                if (pos["seen"] and np.isfinite(hi) and hi < 0) or di == -1:
                    lx[i] = True
                    pos = None
            else:
                if np.isfinite(hi) and hi < 0:
                    pos["seen"] = True
                if (pos["seen"] and np.isfinite(hi) and hi > 0) or di == 1:
                    sx[i] = True
                    pos = None
        if pos is None:
            if di == 1:
                le[i] = True
                pos = {"side": "long", "seen": np.isfinite(hi) and hi > 0}
            elif di == -1:
                se[i] = True
                pos = {"side": "short", "seen": np.isfinite(hi) and hi < 0}

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
