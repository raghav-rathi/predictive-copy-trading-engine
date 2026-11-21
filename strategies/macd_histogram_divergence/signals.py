"""MACD Histogram Divergence signals.

Long entry:  bullish divergence confirmation.
Short entry: bearish divergence confirmation.
Long exit:   bearish divergence confirmation OR hist crosses below 0.
Short exit:  bullish divergence confirmation OR hist crosses above 0.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hist = df["macd_hist"]
    bull = df["bull_div"].fillna(False).astype(bool)
    bear = df["bear_div"].fillna(False).astype(bool)
    cross_up = B.crossed_above(hist, 0).fillna(False).astype(bool)
    cross_dn = B.crossed_below(hist, 0).fillna(False).astype(bool)
    df["long_entry"] = bull
    df["short_entry"] = bear
    df["long_exit"] = (bear | cross_dn).astype(bool)
    df["short_exit"] = (bull | cross_up).astype(bool)
    return df
