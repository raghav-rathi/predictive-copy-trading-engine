"""Heikin Ashi delta sign-change signals.

    delta = HA_close - HA_open

    long_entry  = delta crosses from negative to positive
                  (equivalently: delta > 0 after >= 3 bars negative)
                  AND HA_close > HA_open (same as delta > 0)
    short_entry = delta crosses from positive to negative
                  AND HA_close < HA_open
    long_exit   = delta crosses back through zero (below)
    short_exit  = delta crosses back through zero (above)

The ">= 3 bars negative" clause is folded into the cross: a cross from
negative to positive after a run of negative bars is exactly
crossed_above(delta, 0). The explicit run-length form is OR-ed in so
a jump that skips the exact crossing bar (e.g. a gap in delta) still
registers — both forms are no-lookahead.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = df["ha_delta"]
    cross_up = crossed_above(d, 0).fillna(False)
    cross_dn = crossed_below(d, 0).fillna(False)
    # delta > 0 after >= 3 consecutive negative bars (covers jumps that
    # skip the exact crossing bar; the cross already covers the rest).
    neg_run = (d.shift(1) < 0) & (d.shift(2) < 0) & (d.shift(3) < 0)
    pos_run = (d.shift(1) > 0) & (d.shift(2) > 0) & (d.shift(3) > 0)
    long_turn = (cross_up | ((d > 0) & neg_run)).fillna(False)
    short_turn = (cross_dn | ((d < 0) & pos_run)).fillna(False)
    df["long_entry"] = (long_turn & (df["ha_close"] > df["ha_open"])).astype(bool)
    df["short_entry"] = (short_turn & (df["ha_close"] < df["ha_open"])).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
