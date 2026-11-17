"""RSI + volume-confirmation signals.

Long entry:  RSI crosses above 50 AND volume > 1.25x trailing
             20-bar mean volume.
Short entry: RSI crosses below 50 AND volume > 1.25x trailing
             20-bar mean volume.
Long exit:   RSI crosses below 50.
Short exit:  RSI crosses above 50.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = B.crossed_above(df["rsi"], 50.0).fillna(False)
    cross_dn = B.crossed_below(df["rsi"], 50.0).fillna(False)
    vol_ok = (df["vol_ratio"] > 1.25).fillna(False)
    df["long_entry"] = (cross_up & vol_ok).astype(bool)
    df["short_entry"] = (cross_dn & vol_ok).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
