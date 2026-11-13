"""Pairs-trading spread signals (Gatev, Goetzmann & Rouwenhorst, 2006).

The traded instrument is the synthetic BTC-ETH spread (see
indicators.py): a long spread position is long BTC / short ETH,
a short spread position is the reverse. Positions are entered on
a 2-sigma dislocation and exited when the z-score mean-reverts
through zero.

    Long spread entry:  z crosses below -2
    Short spread entry: z crosses above +2
    Long spread exit:   z crosses above 0
    Short spread exit:  z crosses below 0

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open). The harness risk layer's
2xATR stop / 2.5xATR trail / 120-bar max hold also applies.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    z = df["z"]
    long_entry = B.crossed_below(z, -2.0)
    short_entry = B.crossed_above(z, 2.0)
    long_exit = B.crossed_above(z, 0.0)
    short_exit = B.crossed_below(z, 0.0)
    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = long_exit.fillna(False).astype(bool)
    df["short_exit"] = short_exit.fillna(False).astype(bool)
    return df
