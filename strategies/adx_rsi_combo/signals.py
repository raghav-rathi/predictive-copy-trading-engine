"""ADX + RSI combo signals.

Long entry:  RSI(14) crosses above 30 AND ADX(14) > 25.
Short entry: RSI(14) crosses below 70 AND ADX(14) > 25.
Long exit:   RSI(14) crosses back below 50.
Short exit:  RSI(14) crosses back above 50.

The ADX filter is evaluated on the same bar as the RSI cross (both
are known at bar i's close). The exits are pure RSI midline crosses:
no ADX condition, so a position is closed as soon as momentum fades
back through 50 even if the trend is still "strong" by ADX.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsi = df["rsi"]
    adx = df["adx"]
    trend = (adx > 25).fillna(False)
    df["long_entry"] = (B.crossed_above(rsi, 30) & trend).fillna(False).astype(bool)
    df["short_entry"] = (B.crossed_below(rsi, 70) & trend).fillna(False).astype(bool)
    df["long_exit"] = B.crossed_below(rsi, 50).fillna(False).astype(bool)
    df["short_exit"] = B.crossed_above(rsi, 50).fillna(False).astype(bool)
    return df
