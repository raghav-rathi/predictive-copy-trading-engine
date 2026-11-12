"""Vortex + ADX signals.

Long entry:  VI+ crosses above VI- with ADX(14) > 25.
Short entry: VI- crosses above VI+ with ADX(14) > 25.
Long exit:   the opposite VI cross, or ADX(14) < 20.
Short exit:  the opposite VI cross, or ADX(14) < 20.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies, so
in practice most positions end on the stop/trail/max-hold before the
signal exit; the VI cross / ADX fade is the system-defined exit.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

ADX_STRONG = 25
ADX_WEAK = 20


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = crossed_above(df["vi_plus"], df["vi_minus"]).fillna(False)
    cross_dn = crossed_below(df["vi_plus"], df["vi_minus"]).fillna(False)
    strong = (df["adx"] > ADX_STRONG).fillna(False)
    weak = (df["adx"] < ADX_WEAK).fillna(False)
    df["long_entry"] = (cross_up & strong).astype(bool)
    df["short_entry"] = (cross_dn & strong).astype(bool)
    df["long_exit"] = (cross_dn | weak).astype(bool)
    df["short_exit"] = (cross_up | weak).astype(bool)
    return df
