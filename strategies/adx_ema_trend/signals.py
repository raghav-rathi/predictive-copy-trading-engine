"""EMA crossover + ADX filter signals.

Long entry:  EMA(20) crosses above EMA(50) AND ADX > 25 AND +DI > -DI.
Short entry: EMA(20) crosses below EMA(50) AND ADX > 25 AND -DI > +DI.
Long exit:   EMA(20) crosses below EMA(50) OR ADX < 20.
Short exit:  EMA(20) crosses above EMA(50) OR ADX < 20.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = B.crossed_above(df["ema20"], df["ema50"]).fillna(False)
    cross_dn = B.crossed_below(df["ema20"], df["ema50"]).fillna(False)
    adx_strong = (df["adx"] > 25).fillna(False)
    adx_weak = (df["adx"] < 20).fillna(False)
    plus_dom = (df["plus_di"] > df["minus_di"]).fillna(False)
    minus_dom = (df["minus_di"] > df["plus_di"]).fillna(False)
    df["long_entry"] = (cross_up & adx_strong & plus_dom).astype(bool)
    df["short_entry"] = (cross_dn & adx_strong & minus_dom).astype(bool)
    df["long_exit"] = (cross_dn | adx_weak).astype(bool)
    df["short_exit"] = (cross_up | adx_weak).astype(bool)
    return df
