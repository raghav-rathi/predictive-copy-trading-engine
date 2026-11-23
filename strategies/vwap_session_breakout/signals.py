"""UTC-day session VWAP breakout signals (intraday VWAP system).

LONG on the close breaking above VWAP + 1.0 SD (transition:
close crosses above the upper band) with the bar's volume above
the session's average bar volume.
SHORT on the mirror: close breaking below VWAP - 1.0 SD with
above-average volume.

Exits (state machine, transition-only entries, no re-entry on a
held state):
- Long: close back below VWAP (the breakout failed / the
  session mean reclaimed price).
- Short: close back above VWAP.
- An opposite entry condition while in a position flips it
  (exit + entry on the same bar).

Entries are only considered from the 3rd bar of a session
onward (see indicators.py): on the first bars the volume-
weighted SD is computed from 1-2 points and the band is not a
meaningful breakout level.

No ADX or other regime filter by design — this build tests the
raw VWAP breakout, unlike vwap_bollinger_bands, which fades the
bands only when ADX(14) < 25.

All conditions read bar-i values at bar i; signal columns are
boolean, no NaN, no lookahead (the harness executes at the next
bar's open).
"""

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.vwap_session_breakout.indicators import MIN_SESSION_BARS


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    vwap = df["vwap"].to_numpy(dtype=float)
    upper = df["vwap_upper"].to_numpy(dtype=float)
    lower = df["vwap_lower"].to_numpy(dtype=float)
    session_bar = df["session_bar"].to_numpy(dtype=float)
    vol_above_avg = df["vol_above_avg"].fillna(False).to_numpy(dtype=bool)

    cross_up = B.crossed_above(df["c"], df["vwap_upper"]).fillna(False).to_numpy(dtype=bool)
    cross_down = B.crossed_below(df["c"], df["vwap_lower"]).fillna(False).to_numpy(dtype=bool)
    mature = session_bar >= MIN_SESSION_BARS

    long_setup = cross_up & vol_above_avg & mature
    short_setup = cross_down & vol_above_avg & mature
    long_exit_cond = c < vwap
    short_exit_cond = c > vwap

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short"
    for i in range(n):
        if pos == "long":
            if long_exit_cond[i]:
                lx[i] = True
                pos = None
            elif short_setup[i]:
                lx[i] = True
                se[i] = True
                pos = "short"
        elif pos == "short":
            if short_exit_cond[i]:
                sx[i] = True
                pos = None
            elif long_setup[i]:
                sx[i] = True
                le[i] = True
                pos = "long"
        if pos is None:
            if long_setup[i]:
                le[i] = True
                pos = "long"
            elif short_setup[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
