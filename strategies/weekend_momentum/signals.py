"""Weekend crypto momentum signals.

The source (ACR, "The Weekend Effect in Crypto Momentum",
2020–Apr 2025, 10 majors): 168h momentum long/short signals gated
to weekend sessions — enter Friday 00:00 UTC, exit Sunday 23:59
UTC, flat on weekdays.

- long_entry: momentum > 0 AND the bar is in the weekend session
  (Fri 00:00 – Sun 23:59 UTC), while flat. The harness executes
  at the next bar's open, so an entry signal on the Friday 00:00
  bar fills at the Friday 01:00 open.
- short_entry: the mirror (momentum < 0 AND weekend bar, flat).
- long_exit / short_exit: forced on the first bar after the
  weekend session — the Monday 00:00 UTC bar (executed at the
  Monday 01:00 open; see README.md for the 1-hour slippage this
  implies vs the paper's Sunday 23:59 exit).

One position per weekend: the state machine takes exactly one
entry per weekend session and does not re-enter after a mid-weekend
stop-out — the paper's trade is a single weekend hold, not a
churn of re-entries. (The machine cannot see harness stop-outs, so
after a stop it stays flat until the next weekend; that is the
intended, paper-faithful behaviour.)

All conditions read bar-j closes and bar-j's own UTC timestamp;
the harness executes at the next bar's open. Signal columns are
boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    mom = df["mom168"].fillna(0).to_numpy(dtype=float)
    weekend = df["is_weekend"].fillna(False).to_numpy(dtype=bool)
    monday_open = df["is_monday_open"].fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short" / None
    for i in range(n):
        if pos is not None and monday_open[i]:
            if pos == "long":
                lx[i] = True
            else:
                sx[i] = True
            pos = None
        if pos is None and weekend[i]:
            if mom[i] > 0:
                le[i] = True
                pos = "long"
            elif mom[i] < 0:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
