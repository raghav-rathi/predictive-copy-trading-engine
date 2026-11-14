"""GoNoGo Trend state-transition signals.

    long_entry  = state transitions into Go (>= +1) from neutral/NoGo
                  (prev state <= 0) while the oscillator is positive
    short_entry = state transitions into NoGo (<= -1) from neutral/Go
                  (prev state >= 0) while the oscillator is negative
    long_exit   = state falls back to neutral or worse (state <= 0)
    short_exit  = state rises back to neutral or better (state >= 0)

Entries fire on the *transition* bar, not on every Go bar -- a Go
state that persists for weeks is one trade, entered at its birth.
Exits are state-driven, not first-weakness: a weak Go (+1) still
holds a long; only a return to neutral (amber) or a NoGo flip
closes it. The 2xATR stop / 3xATR trail / 150-bar max hold in
risk.py handles the failure case.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    state = df["gonogo_state"]
    osc = df["gonogo_osc"]
    prev = state.shift(1)

    into_go = (state >= 1) & (prev <= 0)
    into_nogo = (state <= -1) & (prev >= 0)
    # crossed_above/below are kept as the canonical transition check:
    # into_go is exactly "state crossed above 0" when states are -2..+2.
    into_go = into_go & crossed_above(state, 0).fillna(False)
    into_nogo = into_nogo & crossed_below(state, 0).fillna(False)

    df["long_entry"] = (into_go & (osc > 0)).fillna(False).astype(bool)
    df["short_entry"] = (into_nogo & (osc < 0)).fillna(False).astype(bool)
    df["long_exit"] = (state <= 0).fillna(False).astype(bool)
    df["short_exit"] = (state >= 0).fillna(False).astype(bool)
    return df
