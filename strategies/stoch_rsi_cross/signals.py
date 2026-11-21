"""Stochastic RSI Crossover signals.

Long entry:  %K crosses up through %D while %K < 20 (transition only).
Short entry: %K crosses down through %D while %K > 80 (transition only).
Long exit:   %K crosses down through %D.
Short exit:  %K crosses up through %D.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame, long_below: float = 20.0,
                short_above: float = 80.0) -> pd.DataFrame:
    df = df.copy()
    k = df["stoch_k"]
    d = df["stoch_d"]
    pk = k.shift(1)
    pd_ = d.shift(1)
    cross_up = ((k > d) & (pk <= pd_)).fillna(False)
    cross_dn = ((k < d) & (pk >= pd_)).fillna(False)
    df["long_entry"] = (cross_up & (k < long_below)).astype(bool)
    df["short_entry"] = (cross_dn & (k > short_above)).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
