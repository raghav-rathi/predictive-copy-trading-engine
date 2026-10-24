"""ABCD pattern signals.

Enter on pattern completion: long on a bullish ABCD completion bar,
short on a bearish one (the harness executes at the next bar's
open, so the entry lands just after the D pivot confirms).

Exits (state machine over the completion bars, one pass):

- Opposite pattern completion (a bearish ABCD while long, or a
  bullish one while short).
- Pattern failure: price moves 50% of the CD leg BEYOND D against
  the position — long: close <= D - 0.5*CD; short: close >=
  D + 0.5*CD. Half a CD leg past D means the D pivot did not hold
  and the pattern has failed; the harness's 2xATR stop usually
  fires first, this is the signal-level backstop.

The state machine tracks the entry's D price and CD size from the
completion bar, so the failure level survives bars where no new
pattern completes. All conditions read bar-j closes at bar j; the
harness executes at the next bar's open. Signal columns are boolean,
no NaN, no lookahead.
"""

import numpy as np
import pandas as pd

CD_FAIL_FRAC = 0.5  # adverse move past D, as a fraction of CD


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    direction = df["abcd_dir"].fillna(0).to_numpy(dtype=int)
    d_price = df["abcd_d_price"].to_numpy(dtype=float)
    cd = df["abcd_cd"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # dict(side, d_price, cd)
    for i in range(n):
        d = int(direction[i])
        if pos is not None:
            fail = False
            if pos["side"] == "long":
                if d == -1:
                    fail = True
                elif c[i] <= pos["d_price"] - CD_FAIL_FRAC * pos["cd"]:
                    fail = True
                if fail:
                    lx[i] = True
                    pos = None
            else:
                if d == 1:
                    fail = True
                elif c[i] >= pos["d_price"] + CD_FAIL_FRAC * pos["cd"]:
                    fail = True
                if fail:
                    sx[i] = True
                    pos = None
        if pos is None and d != 0:
            if d == 1:
                le[i] = True
                pos = {"side": "long", "d_price": d_price[i], "cd": cd[i]}
            else:
                se[i] = True
                pos = {"side": "short", "d_price": d_price[i], "cd": cd[i]}

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
