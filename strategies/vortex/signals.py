"""Vortex Indicator crossover signals.

Long entry:  VI+ crosses above VI- (buying pressure takes the lead).
Short entry: VI+ crosses below VI- (selling pressure takes the lead).
Long exit:   VI+ crosses back below VI- (the original trigger flips).
Short exit:  VI+ crosses back above VI-.

Pure cross-based, no filter: the Vortex cross IS the trigger in the
Botes/Siepman paper. Exits are the opposite cross, so the strategy is
always aligned with whichever line is on top.

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
    df["long_entry"] = cross_up.astype(bool)
    df["short_entry"] = cross_dn.astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
