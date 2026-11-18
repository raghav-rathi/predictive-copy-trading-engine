"""Supertrend + PSAR agreement signals.

Long entry:  the bar on which price becomes above BOTH lines —
             (c > supertrend) & (c > psar) true now and NOT true on
             the prior bar (agreement turns on).
Short entry: mirror — (c < supertrend) & (c < psar) turns on.
Long exit:   c < supertrend OR c < psar (either tool flips).
Short exit:  c > supertrend OR c > psar.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    above_both = ((df["c"] > df["supertrend"]) & (df["c"] > df["psar"])).fillna(False)
    below_both = ((df["c"] < df["supertrend"]) & (df["c"] < df["psar"])).fillna(False)
    prev_above = above_both.shift(1).fillna(False)
    prev_below = below_both.shift(1).fillna(False)
    df["long_entry"] = (above_both & ~prev_above).astype(bool)
    df["short_entry"] = (below_both & ~prev_below).astype(bool)
    df["long_exit"] = ((df["c"] < df["supertrend"]) | (df["c"] < df["psar"])).fillna(False).astype(bool)
    df["short_exit"] = ((df["c"] > df["supertrend"]) | (df["c"] > df["psar"])).fillna(False).astype(bool)
    return df
