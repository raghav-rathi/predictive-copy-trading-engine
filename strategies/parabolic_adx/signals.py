"""Parabolic SAR flip gated by ADX signals.

Long entry:  PSAR flips from above price to below price on this
             bar (psar < c AND psar.shift(1) > c.shift(1)) AND
             adx > 25 AND plus_di > minus_di.
Short entry: PSAR flips from below to above AND adx > 25 AND
             minus_di > plus_di.
Long exit:   PSAR flips above price OR adx < 20 (trend exhausted).
Short exit:  PSAR flips below price OR adx < 20.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    psar = df["psar"]
    c = df["c"]
    flip_down = ((psar < c) & (psar.shift(1) > c.shift(1))).fillna(False)
    flip_up = ((psar > c) & (psar.shift(1) < c.shift(1))).fillna(False)
    adx_strong = (df["adx"] > 25).fillna(False)
    adx_weak = (df["adx"] < 20).fillna(False)
    plus_gt = (df["plus_di"] > df["minus_di"]).fillna(False)
    minus_gt = (df["minus_di"] > df["plus_di"]).fillna(False)
    df["long_entry"] = (flip_down & adx_strong & plus_gt).astype(bool)
    df["short_entry"] = (flip_up & adx_strong & minus_gt).astype(bool)
    df["long_exit"] = (flip_up | adx_weak).astype(bool)
    df["short_exit"] = (flip_down | adx_weak).astype(bool)
    return df
