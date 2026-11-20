"""Volume-weighted RSI signals.

Long entry:  VW-RSI crosses below 30 (oversold on the
             volume-weighted price).
Short entry: VW-RSI crosses above 70 (overbought).
Long exit:   VW-RSI crosses back above 50.
Short exit:  VW-RSI crosses back below 50.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B

RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
RSI_MID = 50


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsi = df["vw_rsi"]
    df["long_entry"] = B.crossed_below(rsi, RSI_OVERSOLD).fillna(False).astype(bool)
    df["short_entry"] = B.crossed_above(rsi, RSI_OVERBOUGHT).fillna(False).astype(bool)
    df["long_exit"] = B.crossed_above(rsi, RSI_MID).fillna(False).astype(bool)
    df["short_exit"] = B.crossed_below(rsi, RSI_MID).fillna(False).astype(bool)
    return df
