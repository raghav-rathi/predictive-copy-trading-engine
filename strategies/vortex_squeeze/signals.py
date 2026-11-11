"""Vortex crossover signals, gated by a Bollinger BandWidth squeeze.

Long entry:  VI+ crosses above VI- AND the squeeze gate is open
             (squeezing now, or within 5 bars after the squeeze ended).
Short entry: VI+ crosses below VI- AND the squeeze gate is open.
Long exit:   VI+ crosses back below VI- (the opposite cross).
Short exit:  VI+ crosses back above VI-.

This is deliberately a squeeze-gated variant of the plain `vortex`
strategy (precedent: ttm_squeeze, keltner_squeeze): the plain Vortex
cross fires in all regimes, while this one only trades crosses that
follow volatility compression, on the theory that squeezes precede
the directional expansion the cross then confirms.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pos = df["vi_pos"]
    neg = df["vi_neg"]
    cross_up = crossed_above(pos, neg).fillna(False)
    cross_dn = crossed_below(pos, neg).fillna(False)
    gate = df["squeeze_recent"].fillna(False).astype(bool)
    df["long_entry"] = (cross_up & gate).astype(bool)
    df["short_entry"] = (cross_dn & gate).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
